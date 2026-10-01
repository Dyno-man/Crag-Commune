from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from threading import Barrier

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.db import IntegrityError, close_old_connections, transaction
from django.test import RequestFactory, TestCase, TransactionTestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from .models import AuthAttemptBucket
from .rate_limits import client_address, consume_attempts, signup_retry_after

Member = get_user_model()


class AccountTests(TestCase):
    def test_signup_and_private_email(self):
        response = self.client.post(reverse("accounts:signup"), {
            "username": "GraniteGuest",
            "email": "private@example.test",
            "password1": "A-long-unique-test-password-829!",
            "password2": "A-long-unique-test-password-829!",
            "age_eligible": "on",
        })
        self.assertRedirects(response, reverse("accounts:me"))
        member = Member.objects.get(username="GraniteGuest")
        self.assertEqual(member.email, "private@example.test")
        self.assertIsNotNone(member.age_eligible_confirmed_at)
        self.client.post(reverse("accounts:logout"))
        public = self.client.get(reverse("accounts:public_profile", args=["graniteguest"]))
        self.assertEqual(public.status_code, 200)
        self.assertNotContains(public, "private@example.test")
        self.assertNotContains(public, "staff")

    def test_case_insensitive_duplicate_is_rejected(self):
        Member.objects.create_user(username="GraniteGuest", password="A-long-unique-test-password-829!")
        response = self.client.post(reverse("accounts:signup"), {
            "username": "graniteguest",
            "password1": "Another-long-test-password-428!",
            "password2": "Another-long-test-password-428!",
            "age_eligible": "on",
        })
        self.assertContains(response, "already in use")
        self.assertEqual(Member.objects.count(), 1)

    def test_public_name_with_space_can_sign_up_sign_in_and_open_profile(self):
        password = "A-long-unique-test-password-829!"
        response = self.client.post(reverse("accounts:signup"), {
            "username": "Grant V",
            "password1": password,
            "password2": password,
            "age_eligible": "on",
        })
        self.assertRedirects(response, reverse("accounts:me"))
        self.assertTrue(Member.objects.filter(username="Grant V").exists())

        self.client.post(reverse("accounts:logout"))
        self.assertTrue(self.client.login(username="Grant V", password=password))
        profile = self.client.get(reverse("accounts:public_profile", args=["Grant V"]))
        self.assertContains(profile, "Grant V")

    def test_public_name_rejects_repeated_spaces(self):
        for name in ("Grant  V", "Grant\tV"):
            with self.subTest(name=name):
                response = self.client.post(reverse("accounts:signup"), {
                    "username": name,
                    "password1": "A-long-unique-test-password-829!",
                    "password2": "A-long-unique-test-password-829!",
                    "age_eligible": "on",
                })
                self.assertContains(response, "Use letters, digits")
        self.assertEqual(Member.objects.count(), 0)

    def test_signup_requires_age_confirmation_without_collecting_birth_date(self):
        response = self.client.get(reverse("accounts:signup"))
        self.assertContains(response, "at least 13 years old")
        self.assertNotContains(response, "date of birth")
        payload = {
            "username": "NewMember", "password1": "A-long-unique-test-password-829!",
            "password2": "A-long-unique-test-password-829!",
        }
        rejected = self.client.post(reverse("accounts:signup"), payload)
        self.assertContains(rejected, "This field is required")
        self.assertFalse(Member.objects.filter(username="NewMember").exists())
        self.assertFalse(rejected.wsgi_request.user.is_authenticated)
        existing = Member.objects.create_user(username="ExistingMember", password="A-long-unique-test-password-829!")
        self.assertIsNone(existing.age_eligible_confirmed_at)
        self.assertTrue(self.client.login(username="ExistingMember", password="A-long-unique-test-password-829!"))

    def test_database_rejects_case_insensitive_duplicate(self):
        Member.objects.create_user(username="GraniteGuest", password="A-long-unique-test-password-829!")
        with self.assertRaises(IntegrityError), transaction.atomic():
            Member.objects.create_user(username="graniteguest", password="Another-long-test-password-428!")

    def test_public_bio_is_escaped(self):
        Member.objects.create_user(username="Guest", bio="<script>alert(1)</script>", password="A-long-unique-test-password-829!")
        response = self.client.get(reverse("accounts:public_profile", args=["Guest"]))
        self.assertNotContains(response, "<script>")
        self.assertContains(response, "&lt;script&gt;")

    def test_profile_edit_requires_own_login(self):
        owner = Member.objects.create_user(username="Owner", password="A-long-unique-test-password-829!")
        other = Member.objects.create_user(username="Other", password="A-long-unique-test-password-829!")
        self.assertRedirects(self.client.post(reverse("accounts:me"), {"bio": "Changed"}), "/accounts/login/?next=/accounts/me/")
        self.client.force_login(other)
        self.assertRedirects(self.client.post(reverse("accounts:me"), {"bio": "My notes", "home_region": "Chattanooga"}), reverse("accounts:me"))
        owner.refresh_from_db()
        other.refresh_from_db()
        self.assertEqual(owner.bio, "")
        self.assertEqual(other.bio, "My notes")

    def test_logout_requires_post(self):
        member = Member.objects.create_user(username="Guest", password="A-long-unique-test-password-829!")
        self.client.force_login(member)
        self.assertEqual(self.client.get(reverse("accounts:logout")).status_code, 405)
        self.assertRedirects(self.client.post(reverse("accounts:logout")), reverse("home"))

    def test_signup_limit_returns_retry_without_creating_extra_account(self):
        payload = {"username": "", "password1": "bad", "password2": "bad"}
        for _ in range(8):
            self.assertEqual(self.client.post(reverse("accounts:signup"), payload).status_code, 200)
        blocked = self.client.post(reverse("accounts:signup"), payload)
        self.assertEqual(blocked.status_code, 429)
        self.assertContains(blocked, "Too many attempts", status_code=429)
        self.assertIn("Retry-After", blocked)
        self.assertEqual(Member.objects.count(), 0)

    def test_login_name_limit_is_generic_and_independent_of_address(self):
        url = reverse("accounts:login")
        for index in range(12):
            response = self.client.post(url, {"username": "Nobody", "password": "bad"}, REMOTE_ADDR=f"192.0.2.{index + 1}")
            self.assertEqual(response.status_code, 200)
        blocked = self.client.post(url, {"username": "Nobody", "password": "bad"}, REMOTE_ADDR="192.0.2.99")
        self.assertEqual(blocked.status_code, 429)
        self.assertContains(blocked, "Too many attempts", status_code=429)
        self.assertNotContains(blocked, "Nobody", status_code=429)

    @override_settings(TRUSTED_PROXY_IPS=frozenset({"127.0.0.1"}))
    def test_only_explicit_proxy_peer_can_supply_cloudflare_address(self):
        request = RequestFactory().get("/", HTTP_CF_CONNECTING_IP="198.51.100.1", REMOTE_ADDR="203.0.113.9")
        self.assertEqual(client_address(request), "203.0.113.9")
        trusted = RequestFactory().get("/", HTTP_CF_CONNECTING_IP="198.51.100.1", REMOTE_ADDR="127.0.0.1")
        self.assertEqual(client_address(trusted), "198.51.100.1")
        malformed = RequestFactory().get("/", HTTP_CF_CONNECTING_IP="not-an-ip", REMOTE_ADDR="127.0.0.1")
        self.assertEqual(client_address(malformed), "127.0.0.1")

    def test_signup_global_limit_covers_many_addresses(self):
        for index in range(100):
            address = f"198.51.{index // 254}.{index % 254 + 1}"
            request = RequestFactory().post("/accounts/join/", REMOTE_ADDR=address)
            self.assertEqual(signup_retry_after(request), 0)
        extra = RequestFactory().post("/accounts/join/", REMOTE_ADDR="203.0.113.19")
        self.assertGreater(signup_retry_after(extra), 0)

    def test_expired_bucket_resets_and_prune_removes_it(self):
        request = RequestFactory().post("/accounts/join/", REMOTE_ADDR="192.0.2.44")
        self.assertEqual(signup_retry_after(request), 0)
        AuthAttemptBucket.objects.update(expires_at=timezone.now() - timedelta(minutes=1))
        self.assertEqual(signup_retry_after(request), 0)
        self.assertTrue(all(bucket.attempts == 1 for bucket in AuthAttemptBucket.objects.all()))
        AuthAttemptBucket.objects.update(expires_at=timezone.now() - timedelta(minutes=1))
        call_command("prune_auth_attempts", verbosity=0)
        self.assertEqual(AuthAttemptBucket.objects.count(), 0)


class RateLimitConcurrencyTests(TransactionTestCase):
    def test_concurrent_signup_attempts_admit_only_eight(self):
        barrier = Barrier(12)

        def attempt(_index):
            close_old_connections()
            barrier.wait()
            try:
                return consume_attempts([("signup_address", "192.0.2.1")])
            finally:
                close_old_connections()

        with ThreadPoolExecutor(max_workers=12) as pool:
            results = list(pool.map(attempt, range(12)))
        self.assertEqual(sum(result == 0 for result in results), 8)
        self.assertEqual(sum(result > 0 for result in results), 4)
        self.assertEqual(AuthAttemptBucket.objects.get().attempts, 8)
