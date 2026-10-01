from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Q

from .models import MemberBlock


def blocked_member_ids(user):
    if not user.is_authenticated:
        return MemberBlock.objects.none().values_list("blocked_id", flat=True)
    return MemberBlock.objects.filter(blocker=user).values_list("blocked_id", flat=True)


def lock_member_pair(first_id, second_id):
    # The same ordered row locks serialize a block against a new join or acceptance.
    list(get_user_model().objects.select_for_update().filter(
        pk__in=(first_id, second_id)
    ).order_by("pk").values_list("pk", flat=True))


def blocked_between(first_id, second_id):
    return MemberBlock.objects.filter(
        Q(blocker_id=first_id, blocked_id=second_id)
        | Q(blocker_id=second_id, blocked_id=first_id)
    ).exists()


@transaction.atomic
def block_member(blocker, blocked):
    if blocker.pk == blocked.pk:
        raise ValueError("You cannot block yourself.")
    lock_member_pair(blocker.pk, blocked.pk)
    return MemberBlock.objects.get_or_create(blocker=blocker, blocked=blocked)[0]


@transaction.atomic
def unblock_member(blocker, blocked):
    lock_member_pair(blocker.pk, blocked.pk)
    MemberBlock.objects.filter(blocker=blocker, blocked=blocked).delete()
