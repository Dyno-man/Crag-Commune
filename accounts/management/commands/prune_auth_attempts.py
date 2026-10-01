from django.core.management.base import BaseCommand
from django.utils import timezone

from accounts.models import AuthAttemptBucket


class Command(BaseCommand):
    help = "Delete expired signup and login rate-limit records. Run daily."

    def handle(self, *args, **options):
        deleted, _details = AuthAttemptBucket.objects.filter(expires_at__lt=timezone.now()).delete()
        self.stdout.write(f"Deleted {deleted} expired authentication limit records.")
