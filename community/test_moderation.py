from concurrent.futures import ThreadPoolExecutor
from threading import Barrier

from django.contrib.auth import get_user_model
from django.db import close_old_connections
from django.test import TestCase, TransactionTestCase, override_settings
from django.urls import reverse

from .models import DiscussionCategory, DiscussionPost, DiscussionReply, DiscussionReport, ModerationAction, PostingSuspension
from .moderation import ModerationError, decide_report


Member = get_user_model()


@override_settings(DISCUSSION_ENABLED=True)
class ModerationViewTests(TestCase):
    def setUp(self):
        self.owner = Member.objects.create_superuser(username="Owner", password="Long-test-password-129!")
        self.author = Member.objects.create_user(username="Author", password="Long-test-password-129!")
        self.reporter = Member.objects.create_user(username="Reporter", password="Long-test-password-129!")
        category = DiscussionCategory.objects.get(slug="local-questions")
        self.post = DiscussionPost.objects.create(category=category, author=self.author, title="Sample", body="Fictional content")

    def test_only_owner_sees_reports_and_actions(self):
        self.client.force_login(self.reporter)
        report_url = reverse("discussion:report_post", args=[self.post.pk])
        self.assertRedirects(self.client.post(report_url, {"reason": "Please review this fictional post. <script>alert(1)</script>"}), reverse("discussion:detail", args=[self.post.pk]))
        self.assertRedirects(self.client.post(report_url, {"reason": "Another reason"}), reverse("discussion:detail", args=[self.post.pk]))
        report = DiscussionReport.objects.get()
        self.assertIn("Please review this fictional post.", report.reason)
        self.assertEqual(DiscussionReport.objects.count(), 1)
        queue = reverse("discussion:moderation")
        decision = reverse("discussion:moderate_report", args=[report.pk])
        self.assertEqual(self.client.get(queue).status_code, 403)
        self.assertEqual(self.client.post(decision, {"decision": "hide", "reason": "Remove"}).status_code, 403)
        self.client.logout()
        self.assertNotContains(self.client.get(reverse("discussion:detail", args=[self.post.pk])), "Reporter")
        self.client.force_login(self.owner)
        owner_queue = self.client.get(queue)
        self.assertContains(owner_queue, "Please review this fictional post.")
        self.assertNotContains(owner_queue, "<script>alert(1)</script>")

    def test_hide_and_restore_post_are_audited_and_server_enforced(self):
        self.client.force_login(self.reporter)
        self.client.post(reverse("discussion:report_post", args=[self.post.pk]), {"reason": "Needs owner review"})
        report = DiscussionReport.objects.get()
        self.client.force_login(self.owner)
        decision = reverse("discussion:moderate_report", args=[report.pk])
        self.assertRedirects(self.client.post(decision, {"decision": "hide", "reason": "Sensitive detail"}), reverse("discussion:moderation"))
        self.assertRedirects(self.client.post(decision, {"decision": "hide", "reason": "Again"}), reverse("discussion:moderation"))
        self.assertEqual(ModerationAction.objects.count(), 1)
        self.assertEqual(ModerationAction.objects.get().kind, ModerationAction.Kind.HIDE_POST)
        report.refresh_from_db()
        self.assertEqual(report.resolved_by, self.owner)
        self.assertEqual(report.status, DiscussionReport.Status.RESOLVED)
        self.client.logout()
        self.assertEqual(self.client.get(reverse("discussion:detail", args=[self.post.pk])).status_code, 404)
        self.assertNotContains(self.client.get(reverse("discussion:index")), "Sample")
        self.client.force_login(self.owner)
        restore = reverse("discussion:restore_post", args=[self.post.pk])
        self.assertRedirects(self.client.post(restore, {"reason": "Reviewed and cleared"}), reverse("discussion:moderation"))
        self.assertEqual(ModerationAction.objects.count(), 2)
        self.assertContains(self.client.get(reverse("discussion:detail", args=[self.post.pk])), "Sample")

    def test_hide_reply_and_suspend_author_then_restore(self):
        reply = DiscussionReply.objects.create(post=self.post, author=self.author, body="Fictional reply")
        self.client.force_login(self.reporter)
        self.client.post(reverse("discussion:report_reply", args=[self.post.pk, reply.pk]), {"reason": "Review reply"})
        report = DiscussionReport.objects.get()
        self.client.force_login(self.owner)
        decision = reverse("discussion:moderate_report", args=[report.pk])
        self.client.post(decision, {"decision": "hide", "reason": "Hide reply"})
        self.client.logout()
        self.assertNotContains(self.client.get(reverse("discussion:detail", args=[self.post.pk])), "Fictional reply")
        self.client.force_login(self.owner)
        self.client.post(reverse("discussion:restore_reply", args=[reply.pk]), {"reason": "Rechecked"})
        self.assertContains(self.client.get(reverse("discussion:detail", args=[self.post.pk])), "Fictional reply")

        second_report = DiscussionReport.objects.create(reporter=self.reporter, post=self.post, reason="Repeated problem")
        self.client.post(reverse("discussion:moderate_report", args=[second_report.pk]), {"decision": "suspend", "reason": "Repeated posts"})
        self.assertTrue(PostingSuspension.objects.get(member=self.author).is_suspended)
        self.client.force_login(self.author)
        self.assertEqual(self.client.post(reverse("discussion:create"), {
            "category": self.post.category_id, "title": "Another", "body": "Body",
        }).status_code, 403)
        self.assertEqual(self.client.post(reverse("discussion:reply", args=[self.post.pk]), {"body": "Blocked"}).status_code, 403)
        self.client.force_login(self.owner)
        self.client.post(reverse("discussion:restore_account", args=[self.author.pk]), {"reason": "Suspension ended"})
        self.assertFalse(PostingSuspension.objects.get(member=self.author).is_suspended)
        self.client.force_login(self.author)
        self.assertRedirects(self.client.post(reverse("discussion:reply", args=[self.post.pk]), {"body": "Allowed"}), reverse("discussion:detail", args=[self.post.pk]))

    def test_invalid_reports_and_forged_targets_do_not_create_records(self):
        self.client.force_login(self.reporter)
        report_url = reverse("discussion:report_post", args=[self.post.pk])
        self.assertEqual(self.client.post(report_url, {"reason": "x" * 501}).status_code, 400)
        self.assertEqual(self.client.post(reverse("discussion:report_post", args=[99999]), {"reason": "Missing"}).status_code, 404)
        self.assertEqual(self.client.post(reverse("discussion:report_reply", args=[self.post.pk, 99999]), {"reason": "Missing"}).status_code, 404)
        self.assertEqual(DiscussionReport.objects.count(), 0)
        self.client.force_login(self.author)
        self.assertEqual(self.client.post(report_url, {"reason": "Own post"}).status_code, 403)
        self.assertEqual(DiscussionReport.objects.count(), 0)


class ClosedModerationTests(TestCase):
    def test_moderation_routes_are_closed_with_discussion(self):
        owner = Member.objects.create_superuser(username="Owner", password="Long-test-password-129!")
        self.client.force_login(owner)
        self.assertEqual(self.client.get(reverse("discussion:moderation")).status_code, 404)
        self.assertEqual(self.client.post(reverse("discussion:moderate_report", args=[1]), {
            "decision": "dismiss", "reason": "No report",
        }).status_code, 404)


class ModerationConcurrencyTests(TransactionTestCase):
    def test_concurrent_decisions_record_one_action(self):
        owner = Member.objects.create_superuser(username="Owner", password="Long-test-password-129!")
        author = Member.objects.create_user(username="Author", password="Long-test-password-129!")
        reporter = Member.objects.create_user(username="Reporter", password="Long-test-password-129!")
        # Earlier TransactionTestCase classes flush migration seed rows.
        category, _ = DiscussionCategory.objects.get_or_create(
            slug="local-questions", defaults={"name": "Local questions"}
        )
        post = DiscussionPost.objects.create(category=category, author=author, title="Fictional", body="Fictional")
        report = DiscussionReport.objects.create(reporter=reporter, post=post, reason="Review")
        barrier = Barrier(2)

        def decide(_index):
            close_old_connections()
            barrier.wait()
            try:
                decide_report(report.pk, owner, "dismiss", "Reviewed")
                return "resolved"
            except ModerationError:
                return "already handled"
            finally:
                close_old_connections()

        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(decide, range(2)))
        self.assertCountEqual(results, ["resolved", "already handled"])
        self.assertEqual(ModerationAction.objects.filter(report=report).count(), 1)
