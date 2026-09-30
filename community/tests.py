from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from threading import Barrier
from zoneinfo import ZoneInfo

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import close_old_connections
from django.test import TestCase, TransactionTestCase
from django.urls import reverse
from django.utils import timezone

from .forms import parse_local_time
from .models import Outing, Participation
from .services import ParticipationError, host_decide, request_to_join


Member = get_user_model()


def sample_outing(host, **kwargs):
    start = timezone.now() + timedelta(days=1)
    return Outing.objects.create(
        host=host,
        title="Saturday bouldering",
        description="Easy pace and room for new partners.",
        starts_at=start,
        ends_at=start + timedelta(hours=3),
        private_meetup="Private meeting clue",
        **kwargs,
    )


class OutingViewTests(TestCase):
    def setUp(self):
        self.host = Member.objects.create_user(username="Host", password="Long-test-password-129!")
        self.guest = Member.objects.create_user(username="Guest", password="Long-test-password-129!")
        self.outing = sample_outing(self.host, capacity=2)

    def test_public_and_pending_members_cannot_see_private_details(self):
        detail = reverse("community:detail", args=[self.outing.pk])
        public = self.client.get(detail)
        self.assertEqual(public.status_code, 200)
        self.assertNotContains(public, "Private meeting clue")
        self.assertNotContains(public, "People joining")
        self.client.force_login(self.guest)
        self.assertRedirects(self.client.post(reverse("community:join", args=[self.outing.pk])), detail)
        pending = self.client.get(detail)
        self.assertNotContains(pending, "Private meeting clue")
        self.assertNotContains(pending, "People joining")
        participation = Participation.objects.get(outing=self.outing, member=self.guest)
        self.assertEqual(participation.status, Participation.Status.REQUESTED)
        self.client.force_login(self.host)
        self.client.post(reverse("community:accept", args=[self.outing.pk, participation.pk]))
        self.client.force_login(self.guest)
        accepted = self.client.get(detail)
        self.assertContains(accepted, "Private meeting clue")
        self.assertContains(accepted, "People joining")

    def test_non_host_cannot_accept_or_see_requests(self):
        third = Member.objects.create_user(username="Third", password="Long-test-password-129!")
        participation = Participation.objects.create(outing=self.outing, member=third, status=Participation.Status.REQUESTED)
        self.client.force_login(self.guest)
        detail = self.client.get(reverse("community:detail", args=[self.outing.pk]))
        self.assertNotContains(detail, "Join requests")
        self.client.post(reverse("community:accept", args=[self.outing.pk, participation.pk]))
        participation.refresh_from_db()
        self.assertEqual(participation.status, Participation.Status.REQUESTED)

    def test_join_requires_login_and_post(self):
        join_url = reverse("community:join", args=[self.outing.pk])
        self.assertRedirects(self.client.post(join_url), f"/accounts/login/?next={join_url}")
        self.client.force_login(self.guest)
        self.assertEqual(self.client.get(join_url).status_code, 405)
        self.assertFalse(Participation.objects.filter(outing=self.outing, member=self.guest).exists())

    def test_open_outing_auto_accepts_only_until_full(self):
        self.outing.join_policy = Outing.JoinPolicy.OPEN
        self.outing.save(update_fields=["join_policy"])
        first = request_to_join(self.outing.pk, self.guest)
        third = Member.objects.create_user(username="Third", password="Long-test-password-129!")
        second = request_to_join(self.outing.pk, third)
        self.assertEqual(first.status, Participation.Status.ACCEPTED)
        self.assertEqual(second.status, Participation.Status.WAITLISTED)
        self.assertEqual(self.outing.spaces_left(), 0)

    def test_member_can_create_stone_fort_outing(self):
        self.client.force_login(self.guest)
        local_start = timezone.localtime(timezone.now() + timedelta(days=2), ZoneInfo("America/New_York")).replace(minute=0, second=0, microsecond=0)
        response = self.client.post(reverse("community:create"), {
            "title": "New session",
            "description": "Climb together.",
            "capacity": 3,
            "join_policy": "request",
            "private_meetup": "At the agreed meeting point",
            "start_local": local_start.strftime("%Y-%m-%dT%H:%M"),
            "end_local": (local_start + timedelta(hours=2)).strftime("%Y-%m-%dT%H:%M"),
        })
        self.assertEqual(response.status_code, 302)
        created = Outing.objects.get(title="New session")
        self.assertEqual(created.host, self.guest)
        self.assertEqual(created.time_zone, "America/New_York")

    def test_clock_change_time_is_rejected(self):
        with self.assertRaises(ValidationError):
            parse_local_time("2027-03-14T02:30")


class CapacityConcurrencyTests(TransactionTestCase):
    def test_two_acceptances_cannot_fill_one_space(self):
        host = Member.objects.create_user(username="Host", password="Long-test-password-129!")
        first = Member.objects.create_user(username="First", password="Long-test-password-129!")
        second = Member.objects.create_user(username="Second", password="Long-test-password-129!")
        outing = sample_outing(host, capacity=2)
        first_request = Participation.objects.create(outing=outing, member=first, status=Participation.Status.REQUESTED)
        second_request = Participation.objects.create(outing=outing, member=second, status=Participation.Status.REQUESTED)
        barrier = Barrier(2)

        def attempt(participation_id):
            close_old_connections()
            barrier.wait()
            try:
                host_decide(outing.pk, participation_id, host, True)
                return "accepted"
            except ParticipationError:
                return "full"
            finally:
                close_old_connections()

        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(attempt, [first_request.pk, second_request.pk]))
        self.assertCountEqual(results, ["accepted", "full"])
        self.assertEqual(outing.accepted_count(), 1)
