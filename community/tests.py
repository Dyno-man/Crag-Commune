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
from .models import Outing, OutingNotice, OutingRevision, Participation
from .services import ParticipationError, cancel_outing, host_decide, request_to_join


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

    def test_two_accounts_join_then_receive_private_cancellation_notice(self):
        password = "Long-test-password-129!"
        for username in ("PilotHost", "PilotGuest"):
            response = self.client.post(reverse("accounts:signup"), {
                "username": username,
                "password1": password,
                "password2": password,
            })
            self.assertRedirects(response, reverse("accounts:me"))
            self.client.post(reverse("accounts:logout"))

        host = Member.objects.get(username="PilotHost")
        guest = Member.objects.get(username="PilotGuest")
        outing = sample_outing(host, capacity=2)
        outing.title = "Cancelled pilot session"
        outing.save(update_fields=["title"])
        detail_url = reverse("community:detail", args=[outing.pk])
        cancel_url = reverse("community:cancel", args=[outing.pk])

        self.client.login(username=guest.username, password=password)
        self.assertRedirects(self.client.post(reverse("community:join", args=[outing.pk])), detail_url)
        participation = Participation.objects.get(outing=outing, member=guest)
        self.assertEqual(participation.status, Participation.Status.REQUESTED)
        self.assertNotContains(self.client.get(detail_url), "Private meeting clue")
        self.assertEqual(self.client.get(cancel_url).status_code, 403)
        self.assertEqual(self.client.post(cancel_url).status_code, 403)

        self.client.post(reverse("accounts:logout"))
        self.client.login(username=host.username, password=password)
        self.client.post(reverse("community:accept", args=[outing.pk, participation.pk]))
        participation.refresh_from_db()
        self.assertEqual(participation.status, Participation.Status.ACCEPTED)
        self.assertContains(self.client.get(cancel_url), "Confirm cancellation")
        self.assertRedirects(self.client.post(cancel_url, {"note": "Plans changed; please stay home."}), detail_url)
        self.assertRedirects(self.client.post(cancel_url, {"note": "Different note"}), detail_url)
        outing.refresh_from_db()
        self.assertEqual(outing.status, Outing.Status.CANCELLED)
        self.assertEqual(outing.cancelled_by, host)
        self.assertIsNotNone(outing.cancelled_at)
        self.assertEqual(OutingNotice.objects.filter(outing=outing, recipient=guest).count(), 1)
        self.assertNotContains(self.client.get(reverse("community:list")), outing.title)

        self.client.post(reverse("accounts:logout"))
        public = self.client.get(detail_url)
        self.assertContains(public, "This outing was cancelled")
        self.assertNotContains(public, "Plans changed")
        self.assertNotContains(public, "Private meeting clue")

        self.client.login(username=guest.username, password=password)
        self.assertContains(self.client.get(reverse("community:notices")), outing.title)
        self.assertContains(self.client.get(detail_url), "Plans changed; please stay home.")
        self.assertNotContains(self.client.get(detail_url), "Private meeting clue")
        self.client.post(reverse("community:join", args=[outing.pk]))
        self.assertEqual(OutingNotice.objects.filter(outing=outing, recipient=guest).count(), 1)

    def test_pending_member_gets_no_cancellation_notice(self):
        self.client.force_login(self.guest)
        self.client.post(reverse("community:join", args=[self.outing.pk]))
        self.client.force_login(self.host)
        cancel_outing(self.outing.pk, self.host, "Private cancellation note")
        self.client.force_login(self.guest)
        self.assertFalse(OutingNotice.objects.filter(outing=self.outing, recipient=self.guest).exists())
        self.assertNotContains(self.client.get(reverse("community:notices")), self.outing.title)
        self.assertNotContains(self.client.get(reverse("community:detail", args=[self.outing.pk])), "Private cancellation note")

    def edit_payload(self, **overrides):
        start = self.outing.starts_at.astimezone(ZoneInfo("America/New_York"))
        payload = {
            "title": self.outing.title,
            "description": self.outing.description,
            "start_local": start.strftime("%Y-%m-%dT%H:%M"),
            "end_local": (start + timedelta(hours=3)).strftime("%Y-%m-%dT%H:%M"),
            "capacity": self.outing.capacity,
            "join_policy": self.outing.join_policy,
            "private_meetup": self.outing.private_meetup,
            "version": self.outing.version,
        }
        payload.update(overrides)
        return payload

    def test_host_edit_notifies_accepted_members_and_keeps_history_private(self):
        pending = Member.objects.create_user(username="Pending", password="Long-test-password-129!")
        Participation.objects.create(outing=self.outing, member=self.guest, status=Participation.Status.ACCEPTED)
        Participation.objects.create(outing=self.outing, member=pending, status=Participation.Status.REQUESTED)
        edit_url = reverse("community:edit", args=[self.outing.pk])
        detail_url = reverse("community:detail", args=[self.outing.pk])
        self.client.force_login(self.guest)
        self.assertEqual(self.client.get(edit_url).status_code, 403)
        self.assertEqual(self.client.post(edit_url, self.edit_payload(title="New title")).status_code, 403)

        self.client.force_login(self.host)
        form = self.client.get(edit_url)
        self.assertContains(form, 'name="version"')
        self.assertContains(form, 'name="start_local"')
        change = self.edit_payload(title="New title", private_meetup="New private clue")
        rejected = self.client.post(edit_url, change)
        self.assertContains(rejected, "Acknowledge that accepted members")
        self.assertEqual(OutingRevision.objects.count(), 0)
        change["acknowledge_change"] = "on"
        self.assertRedirects(self.client.post(edit_url, change), detail_url)
        self.outing.refresh_from_db()
        self.assertEqual(self.outing.version, 2)
        self.assertEqual(self.outing.title, "New title")
        self.assertEqual(OutingRevision.objects.count(), 1)
        self.assertEqual(OutingNotice.objects.filter(recipient=self.guest, kind=OutingNotice.Kind.CHANGED).count(), 1)
        self.assertFalse(OutingNotice.objects.filter(recipient=pending).exists())
        self.assertContains(self.client.get(detail_url), "New private clue")

        self.client.force_login(self.guest)
        self.assertContains(self.client.get(reverse("community:notices")), "Outing changed")
        accepted_detail = self.client.get(detail_url)
        self.assertContains(accepted_detail, "Change history")
        self.assertContains(accepted_detail, "Private meeting clue")
        self.assertContains(accepted_detail, "New private clue")
        self.client.force_login(pending)
        self.assertNotContains(self.client.get(detail_url), "New private clue")
        self.assertNotContains(self.client.get(detail_url), "Private meeting clue")
        self.assertNotContains(self.client.get(detail_url), "Change history")
        self.client.logout()
        self.assertNotContains(self.client.get(detail_url), "Change history")
        self.assertNotContains(self.client.get(detail_url), "New private clue")

    def test_edit_rejects_stale_version_and_capacity_below_accepted_count(self):
        Participation.objects.create(outing=self.outing, member=self.guest, status=Participation.Status.ACCEPTED)
        self.client.force_login(self.host)
        edit_url = reverse("community:edit", args=[self.outing.pk])
        too_small = self.client.post(edit_url, self.edit_payload(capacity=1, acknowledge_change="on"))
        self.assertContains(too_small, "Capacity cannot be less")
        self.assertEqual(OutingRevision.objects.count(), 0)
        self.client.post(edit_url, self.edit_payload(title="First edit", acknowledge_change="on"))
        stale = self.client.post(edit_url, self.edit_payload(title="Stale edit", acknowledge_change="on"))
        self.assertContains(stale, "changed while you were editing")
        self.outing.refresh_from_db()
        self.assertEqual(self.outing.title, "First edit")
        self.assertEqual(OutingRevision.objects.count(), 1)
        self.assertEqual(OutingNotice.objects.filter(recipient=self.guest, kind=OutingNotice.Kind.CHANGED).count(), 1)


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
