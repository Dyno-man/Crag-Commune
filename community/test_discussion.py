from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import DiscussionCategory, DiscussionPost, DiscussionReply


Member = get_user_model()


class ClosedDiscussionTests(TestCase):
    def test_all_discussion_routes_are_closed_by_default(self):
        member = Member.objects.create_user(username="Pilot", password="Long-test-password-129!")
        category = DiscussionCategory.objects.get(slug="local-questions")
        post = DiscussionPost.objects.create(category=category, author=member, title="Question", body="Sample")
        self.client.force_login(member)
        for url, method in (
            (reverse("discussion:index"), "get"),
            (reverse("discussion:create"), "get"),
            (reverse("discussion:create"), "post"),
            (reverse("discussion:detail", args=[post.pk]), "get"),
            (reverse("discussion:reply", args=[post.pk]), "post"),
        ):
            with self.subTest(url=url, method=method):
                self.assertEqual(getattr(self.client, method)(url).status_code, 404)
        self.assertEqual(DiscussionPost.objects.count(), 1)
        self.assertEqual(DiscussionReply.objects.count(), 0)
        self.assertNotContains(self.client.get(reverse("home")), "Discussion</a>")


@override_settings(DISCUSSION_ENABLED=True)
class DiscussionViewTests(TestCase):
    def setUp(self):
        self.author = Member.objects.create_user(username="Pilot", password="Long-test-password-129!")
        self.reader = Member.objects.create_user(username="Reader", password="Long-test-password-129!")
        self.category = DiscussionCategory.objects.get(slug="local-questions")

    def test_seeded_categories_and_public_reading(self):
        self.assertEqual(DiscussionCategory.objects.count(), 4)
        post = DiscussionPost.objects.create(
            category=self.category, author=self.author, title="Weather question", body="Personal observation only."
        )
        listing = self.client.get(reverse("discussion:index"))
        self.assertContains(listing, "Weather question")
        self.assertContains(listing, "Find partners")
        self.assertContains(self.client.get(reverse("discussion:detail", args=[post.pk])), "Personal observation only.")
        self.assertContains(self.client.get(reverse("home")), "Discussion</a>")

    def test_login_required_and_post_reply_are_attributed(self):
        create_url = reverse("discussion:create")
        self.assertRedirects(self.client.get(create_url), f"/accounts/login/?next={create_url}")
        self.client.force_login(self.author)
        response = self.client.post(create_url, {
            "category": self.category.pk, "title": "Find a partner", "body": "Personal experience."
        })
        post = DiscussionPost.objects.get(title="Find a partner")
        self.assertRedirects(response, reverse("discussion:detail", args=[post.pk]))
        self.assertEqual(post.author, self.author)
        reply_url = reverse("discussion:reply", args=[post.pk])
        self.client.logout()
        self.assertRedirects(self.client.post(reply_url, {"body": "Hello"}), f"/accounts/login/?next={reply_url}")
        self.client.force_login(self.reader)
        self.assertEqual(self.client.get(reply_url).status_code, 405)
        self.assertRedirects(self.client.post(reply_url, {"body": "I can join."}), reverse("discussion:detail", args=[post.pk]))
        self.assertEqual(DiscussionReply.objects.get(post=post).author, self.reader)

    def test_filter_search_and_hidden_content(self):
        public = DiscussionPost.objects.create(category=self.category, author=self.author, title="Question", body="Chalk bag")
        other = DiscussionCategory.objects.get(slug="find-partners")
        hidden = DiscussionPost.objects.create(category=other, author=self.author, title="Hidden", body="Secret", is_hidden=True)
        listing = self.client.get(reverse("discussion:index"), {"category": self.category.slug, "q": "chalk"})
        self.assertContains(listing, "Question")
        self.assertNotContains(listing, "Hidden")
        self.assertEqual(self.client.get(reverse("discussion:detail", args=[hidden.pk])).status_code, 404)
        DiscussionReply.objects.create(post=public, author=self.reader, body="Private hidden reply", is_hidden=True)
        self.assertNotContains(self.client.get(reverse("discussion:detail", args=[public.pk])), "Private hidden reply")

    def test_html_escapes_and_oversized_content_is_rejected(self):
        self.client.force_login(self.author)
        create_url = reverse("discussion:create")
        oversized = self.client.post(create_url, {
            "category": self.category.pk, "title": "Too long", "body": "x" * 3001,
        })
        self.assertContains(oversized, "at most 3000 characters")
        self.assertEqual(DiscussionPost.objects.count(), 0)
        self.client.post(create_url, {
            "category": self.category.pk, "title": "<script>alert(1)</script>", "body": "<b>not markup</b>",
        })
        post = DiscussionPost.objects.get()
        detail = self.client.get(reverse("discussion:detail", args=[post.pk]))
        self.assertNotContains(detail, "<script>alert(1)</script>")
        self.assertNotContains(detail, "<b>not markup</b>")
        self.assertContains(detail, "&lt;b&gt;not markup&lt;/b&gt;")
        reply_url = reverse("discussion:reply", args=[post.pk])
        bad_reply = self.client.post(reply_url, {"body": "y" * 1501})
        self.assertEqual(bad_reply.status_code, 400)
        self.assertEqual(DiscussionReply.objects.count(), 0)
