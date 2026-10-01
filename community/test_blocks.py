from django.contrib.auth import get_user_model
from concurrent.futures import ThreadPoolExecutor
from threading import Event

from django.db import IntegrityError, close_old_connections, transaction
from django.test import TestCase, TransactionTestCase, override_settings
from django.urls import reverse

from .blocks import block_member, lock_member_pair, unblock_member
from .models import DiscussionCategory, DiscussionPost, DiscussionReply, MemberBlock, Outing, Participation
from .services import ParticipationError, host_decide, request_to_join
from .tests import sample_outing


Member = get_user_model()


class MemberBlockTests(TestCase):
    def setUp(self):
        self.first = Member.objects.create_user(username="First", password="Long-test-password-129!")
        self.second = Member.objects.create_user(username="Second", password="Long-test-password-129!")
        self.third = Member.objects.create_user(username="Third", password="Long-test-password-129!")

    def test_profile_controls_are_private_and_post_only(self):
        profile = reverse("accounts:public_profile", args=[self.second.username])
        block_url = reverse("community:block_member", args=[self.second.username])
        unblock_url = reverse("community:unblock_member", args=[self.second.username])
        self.assertNotContains(self.client.get(profile), "Block member")
        self.assertRedirects(self.client.post(block_url), f"/accounts/login/?next={block_url}")
        self.client.force_login(self.first)
        self.assertEqual(self.client.get(block_url).status_code, 405)
        self.assertContains(self.client.get(profile), "Block member")
        self.assertRedirects(self.client.post(block_url), profile)
        self.assertRedirects(self.client.post(block_url), profile)
        self.assertEqual(MemberBlock.objects.count(), 1)
        self.assertContains(self.client.get(profile), "Unblock member")
        self.assertContains(self.client.get(profile), "Public posts remain visible while signed out")
        self.assertRedirects(self.client.post(unblock_url), profile)
        self.assertFalse(MemberBlock.objects.exists())
        self.client.force_login(self.second)
        self.assertNotContains(self.client.get(profile), "blocked this member")
        self.assertNotContains(self.client.get(reverse("accounts:public_profile", args=[self.second.username])), "Block member")

    def test_self_block_and_duplicate_are_rejected_by_database(self):
        self.client.force_login(self.first)
        self.client.post(reverse("community:block_member", args=[self.first.username]))
        self.assertFalse(MemberBlock.objects.exists())
        block_member(self.first, self.second)
        with self.assertRaises(IntegrityError), transaction.atomic():
            MemberBlock.objects.create(blocker=self.first, blocked=self.second)
        with self.assertRaises(IntegrityError), transaction.atomic():
            MemberBlock.objects.create(blocker=self.first, blocked=self.first)
        unblock_member(self.first, self.second)
        unblock_member(self.first, self.second)
        self.assertFalse(MemberBlock.objects.exists())

    @override_settings(DISCUSSION_ENABLED=True)
    def test_discussion_visibility_for_blocker_and_signed_out_reader(self):
        category = DiscussionCategory.objects.get(slug="local-questions")
        blocked_post = DiscussionPost.objects.create(category=category, author=self.second, title="Blocked title", body="Sample")
        open_post = DiscussionPost.objects.create(category=category, author=self.third, title="Open title", body="Sample")
        DiscussionReply.objects.create(post=open_post, author=self.second, body="Blocked reply")
        DiscussionReply.objects.create(post=open_post, author=self.third, body="Open reply")
        block_member(self.first, self.second)

        self.client.force_login(self.first)
        self.assertNotContains(self.client.get(reverse("discussion:index")), "Blocked title")
        self.assertNotContains(self.client.get(reverse("discussion:index") + "?q=Blocked"), "Blocked title")
        self.assertEqual(self.client.get(reverse("discussion:detail", args=[blocked_post.pk])).status_code, 404)
        self.assertEqual(self.client.post(reverse("discussion:reply", args=[blocked_post.pk]), {"body": "Hi"}).status_code, 404)
        detail = self.client.get(reverse("discussion:detail", args=[open_post.pk]))
        self.assertNotContains(detail, "Blocked reply")
        self.assertContains(detail, "Open reply")
        self.client.logout()
        self.assertContains(self.client.get(reverse("discussion:index")), "Blocked title")
        self.assertContains(self.client.get(reverse("discussion:detail", args=[open_post.pk])), "Blocked reply")
        self.client.force_login(self.second)
        self.assertContains(self.client.get(reverse("discussion:index")), "Blocked title")

    def test_block_stops_new_joins_in_both_directions(self):
        first_outing = sample_outing(self.first, capacity=3, join_policy=Outing.JoinPolicy.OPEN)
        second_outing = sample_outing(self.second, capacity=3, join_policy=Outing.JoinPolicy.OPEN)
        block_member(self.first, self.second)
        with self.assertRaises(ParticipationError):
            request_to_join(first_outing.pk, self.second)
        with self.assertRaises(ParticipationError):
            request_to_join(second_outing.pk, self.first)
        self.assertFalse(Participation.objects.exists())
        self.assertEqual(request_to_join(first_outing.pk, self.third).status, Participation.Status.ACCEPTED)
        unblock_member(self.first, self.second)
        self.assertEqual(request_to_join(first_outing.pk, self.second).status, Participation.Status.ACCEPTED)

    def test_pending_cannot_be_accepted_after_block_and_existing_acceptance_stays(self):
        pending_outing = sample_outing(self.first, capacity=3)
        pending = request_to_join(pending_outing.pk, self.second)
        accepted_outing = sample_outing(self.first, capacity=3, join_policy=Outing.JoinPolicy.OPEN)
        accepted = request_to_join(accepted_outing.pk, self.second)
        self.assertEqual(accepted.status, Participation.Status.ACCEPTED)
        block_member(self.second, self.first)
        with self.assertRaises(ParticipationError):
            host_decide(pending_outing.pk, pending.pk, self.first, True)
        pending.refresh_from_db()
        accepted.refresh_from_db()
        self.assertEqual(pending.status, Participation.Status.REQUESTED)
        self.assertEqual(accepted.status, Participation.Status.ACCEPTED)
        self.assertTrue(accepted_outing.can_view_private(self.second))
        self.assertEqual(request_to_join(accepted_outing.pk, self.second).status, Participation.Status.ACCEPTED)


class BlockJoinConcurrencyTests(TransactionTestCase):
    def test_committed_block_precedes_waiting_join(self):
        host = Member.objects.create_user(username="Host", password="Long-test-password-129!")
        guest = Member.objects.create_user(username="Guest", password="Long-test-password-129!")
        outing = sample_outing(host, join_policy=Outing.JoinPolicy.OPEN)
        pair_locked = Event()
        join_started = Event()

        def block_in_transaction():
            close_old_connections()
            try:
                with transaction.atomic():
                    lock_member_pair(host.pk, guest.pk)
                    pair_locked.set()
                    self.assertTrue(join_started.wait(5))
                    block_member(host, guest)
            finally:
                close_old_connections()

        def join_while_blocking():
            close_old_connections()
            try:
                self.assertTrue(pair_locked.wait(5))
                join_started.set()
                try:
                    request_to_join(outing.pk, guest)
                except ParticipationError:
                    return "blocked"
                return "joined"
            finally:
                close_old_connections()

        with ThreadPoolExecutor(max_workers=2) as pool:
            blocked = pool.submit(block_in_transaction)
            joined = pool.submit(join_while_blocking)
            blocked.result(timeout=10)
            self.assertEqual(joined.result(timeout=10), "blocked")
        self.assertFalse(Participation.objects.filter(outing=outing, member=guest).exists())
