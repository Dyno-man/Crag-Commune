from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.urls import reverse


Member = get_user_model()


class AccountTests(TestCase):
    def test_signup_and_private_email(self):
        response = self.client.post(reverse("accounts:signup"), {
            "username": "GraniteGuest",
            "email": "private@example.test",
            "password1": "A-long-unique-test-password-829!",
            "password2": "A-long-unique-test-password-829!",
        })
        self.assertRedirects(response, reverse("accounts:me"))
        member = Member.objects.get(username="GraniteGuest")
        self.assertEqual(member.email, "private@example.test")
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
        })
        self.assertContains(response, "already in use")
        self.assertEqual(Member.objects.count(), 1)

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
