from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.utils import timezone

from .blocks import blocked_between, lock_member_pair
from .models import Outing, OutingNotice, OutingRevision, Participation


class ParticipationError(Exception):
    pass


class OutingEditError(Exception):
    pass


EDITABLE_OUTING_FIELDS = (
    "title", "description", "starts_at", "ends_at", "capacity", "join_policy", "private_meetup"
)


def revision_value(value):
    return value.isoformat() if hasattr(value, "isoformat") else value


@transaction.atomic
def request_to_join(outing_id, member):
    outing = Outing.objects.select_for_update().get(pk=outing_id)
    if outing.status != Outing.Status.OPEN or member.pk == outing.host_id:
        raise ParticipationError("This outing is not available to join.")
    lock_member_pair(outing.host_id, member.pk)
    participation = Participation.objects.filter(outing=outing, member=member).first()
    if participation and participation.status != Participation.Status.WITHDRAWN:
        return participation
    if blocked_between(outing.host_id, member.pk):
        raise ParticipationError("A member block prevents this join request.")
    if participation is None:
        participation = Participation(outing=outing, member=member)
    if outing.spaces_left() == 0:
        status = Participation.Status.WAITLISTED
    elif outing.join_policy == Outing.JoinPolicy.OPEN:
        status = Participation.Status.ACCEPTED
    else:
        status = Participation.Status.REQUESTED
    participation.status = status
    if participation.pk:
        participation.save(update_fields=["status", "updated_at"])
    else:
        participation.save()
    return participation


@transaction.atomic
def host_decide(outing_id, participation_id, host, accept):
    outing = Outing.objects.select_for_update().get(pk=outing_id)
    if outing.host_id != host.pk or outing.status != Outing.Status.OPEN:
        raise ParticipationError("This action is not available.")
    participation = Participation.objects.select_for_update().get(pk=participation_id, outing=outing)
    if participation.status not in (Participation.Status.REQUESTED, Participation.Status.WAITLISTED):
        raise ParticipationError("This request has already been handled.")
    if accept and outing.spaces_left() == 0:
        raise ParticipationError("The outing is full.")
    if accept:
        lock_member_pair(outing.host_id, participation.member_id)
        if blocked_between(outing.host_id, participation.member_id):
            raise ParticipationError("A member block prevents accepting this request.")
    participation.status = Participation.Status.ACCEPTED if accept else Participation.Status.DECLINED
    participation.save(update_fields=["status", "updated_at"])
    return participation


@transaction.atomic
def withdraw(outing_id, member):
    outing = Outing.objects.select_for_update().get(pk=outing_id)
    participation = Participation.objects.select_for_update().get(outing=outing, member=member)
    if participation.status in (Participation.Status.WITHDRAWN, Participation.Status.DECLINED):
        return participation
    participation.status = Participation.Status.WITHDRAWN
    participation.save(update_fields=["status", "updated_at"])
    return participation


@transaction.atomic
def cancel_outing(outing_id, host, note=""):
    outing = Outing.objects.select_for_update().get(pk=outing_id)
    if outing.host_id != host.pk:
        raise PermissionDenied("Only the host can cancel this outing.")
    if outing.status == Outing.Status.CANCELLED:
        return False
    outing.status = Outing.Status.CANCELLED
    outing.cancelled_at = timezone.now()
    outing.cancelled_by = host
    outing.cancellation_note = note
    outing.save(update_fields=["status", "cancelled_at", "cancelled_by", "cancellation_note"])
    recipients = outing.participations.filter(status=Participation.Status.ACCEPTED).values_list("member_id", flat=True)
    OutingNotice.objects.bulk_create(
        [OutingNotice(outing=outing, recipient_id=recipient_id, kind=OutingNotice.Kind.CANCELLED) for recipient_id in recipients]
    )
    return True


@transaction.atomic
def edit_outing(outing_id, host, candidate, expected_version, acknowledged):
    outing = Outing.objects.select_for_update().get(pk=outing_id)
    if outing.host_id != host.pk:
        raise PermissionDenied("Only the host can edit this outing.")
    if outing.status != Outing.Status.OPEN:
        raise OutingEditError("Cancelled outings cannot be edited.")
    if outing.version != expected_version:
        raise OutingEditError("This outing changed while you were editing it. Reload the page and try again.")

    accepted = list(outing.participations.filter(status=Participation.Status.ACCEPTED).values_list("member_id", flat=True))
    if candidate.capacity < len(accepted) + 1:
        raise OutingEditError("Capacity cannot be less than the host and accepted members already attending.")

    changes = {}
    for field in EDITABLE_OUTING_FIELDS:
        before = getattr(outing, field)
        after = getattr(candidate, field)
        if before != after:
            changes[field] = {"before": revision_value(before), "after": revision_value(after)}
    if not changes:
        return None
    if accepted and not acknowledged:
        raise OutingEditError("Acknowledge that accepted members will be notified before saving these changes.")

    for field in changes:
        setattr(outing, field, getattr(candidate, field))
    outing.version += 1
    outing.save(update_fields=[*changes, "version"])
    revision = OutingRevision.objects.create(outing=outing, changed_by=host, changes=changes)
    OutingNotice.objects.bulk_create(
        [OutingNotice(outing=outing, recipient_id=member_id, revision=revision, kind=OutingNotice.Kind.CHANGED) for member_id in accepted]
    )
    return revision
