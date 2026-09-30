"""Small PostgreSQL-backed admission limits for public authentication forms."""

import hashlib
import hmac
import ipaddress
from datetime import timedelta

from django.conf import settings
from django.db import connection, transaction
from django.utils import timezone

from .models import AuthAttemptBucket


WINDOW = timedelta(minutes=15)
LIMITS = {"signup_address": 8, "signup_global": 100, "login_address": 30, "login_name": 12}


def client_address(request):
    """Only an explicitly trusted direct peer may supply a proxy address."""
    peer = ipaddress.ip_address(request.META["REMOTE_ADDR"])
    if str(peer) in settings.TRUSTED_PROXY_IPS:
        forwarded = request.META.get("HTTP_CF_CONNECTING_IP", "")
        try:
            return str(ipaddress.ip_address(forwarded))
        except ValueError:
            pass
    return str(peer)


def bucket_key(kind, value):
    message = f"auth-limit:{kind}:{value}".encode()
    return hmac.new(settings.SECRET_KEY.encode(), message, hashlib.sha256).hexdigest()


def consume_attempts(items):
    """Atomically admit one request to every bucket, or none of them."""
    buckets = [(bucket_key(kind, value), LIMITS[kind]) for kind, value in items]
    buckets.sort(key=lambda item: item[0])
    now = timezone.now()
    with transaction.atomic():
        # Row locks alone do not protect the first concurrent insert. Advisory
        # transaction locks serialize both existing and new buckets across workers.
        with connection.cursor() as cursor:
            for key, _limit in buckets:
                lock_id = int.from_bytes(bytes.fromhex(key[:16]), "big", signed=True)
                cursor.execute("SELECT pg_advisory_xact_lock(%s)", [lock_id])
        current = []
        for key, limit in buckets:
            bucket, _created = AuthAttemptBucket.objects.get_or_create(
                key=key, defaults={"expires_at": now + WINDOW}
            )
            if bucket.expires_at <= now:
                bucket.attempts = 0
                bucket.expires_at = now + WINDOW
            current.append((bucket, limit))
        remaining = [bucket.expires_at - now for bucket, limit in current if bucket.attempts >= limit]
        if remaining:
            return max(1, int(max(remaining).total_seconds()) + 1)
        for bucket, _limit in current:
            bucket.attempts += 1
            bucket.save(update_fields=["attempts", "expires_at"])
    return 0


def signup_retry_after(request):
    return consume_attempts([
        ("signup_address", client_address(request)),
        ("signup_global", "all"),
    ])


def login_retry_after(request):
    submitted_name = request.POST.get("username", "")[:150].casefold()
    return consume_attempts([
        ("login_address", client_address(request)),
        ("login_name", submitted_name),
    ])
