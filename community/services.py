from django.db import transaction

from .models import Outing, Participation


class ParticipationError(Exception):
    pass


@transaction.atomic
def request_to_join(outing_id, member):
    outing = Outing.objects.select_for_update().get(pk=outing_id)
    if outing.status != Outing.Status.OPEN or member.pk == outing.host_id:
        raise ParticipationError("This outing is not available to join.")
    participation, created = Participation.objects.get_or_create(
        outing=outing, member=member, defaults={"status": Participation.Status.REQUESTED}
    )
    if not created and participation.status != Participation.Status.WITHDRAWN:
        return participation
    if outing.spaces_left() == 0:
        status = Participation.Status.WAITLISTED
    elif outing.join_policy == Outing.JoinPolicy.OPEN:
        status = Participation.Status.ACCEPTED
    else:
        status = Participation.Status.REQUESTED
    participation.status = status
    participation.save(update_fields=["status", "updated_at"])
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
