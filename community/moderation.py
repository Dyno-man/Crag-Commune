from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone

from .models import DiscussionPost, DiscussionReply, DiscussionReport, ModerationAction, PostingSuspension


class ModerationError(Exception):
    pass


def require_owner(actor):
    if not actor.is_authenticated or not actor.is_active or not actor.is_superuser:
        raise PermissionDenied("Only the owner can moderate discussion.")


def can_post(member):
    return member.is_authenticated and member.is_active and not PostingSuspension.objects.filter(
        member=member, is_suspended=True
    ).exists()


@transaction.atomic
def submit_report(reporter, reason, post_id=None, reply_id=None):
    if (post_id is None) == (reply_id is None):
        raise ModerationError("Report exactly one item.")
    if post_id is not None:
        target = get_object_or_404(DiscussionPost.objects.filter(is_hidden=False), pk=post_id)
        if target.author_id == reporter.pk:
            raise ModerationError("You cannot report your own post.")
        lookup = {"post": target}
    else:
        target = get_object_or_404(
            DiscussionReply.objects.filter(is_hidden=False, post__is_hidden=False), pk=reply_id
        )
        if target.author_id == reporter.pk:
            raise ModerationError("You cannot report your own reply.")
        lookup = {"reply": target}
    report, _created = DiscussionReport.objects.get_or_create(
        reporter=reporter, **lookup, defaults={"reason": reason}
    )
    return report


@transaction.atomic
def decide_report(report_id, actor, decision, reason):
    require_owner(actor)
    report = get_object_or_404(DiscussionReport.objects.select_for_update(), pk=report_id)
    if report.status != DiscussionReport.Status.OPEN:
        raise ModerationError("This report has already been handled.")
    if decision not in ("dismiss", "hide", "suspend"):
        raise ModerationError("Unknown moderation decision.")

    post = report.post
    reply = report.reply
    target_author = post.author if post else reply.author
    if decision == "hide":
        target = post or reply
        target = type(target).objects.select_for_update().get(pk=target.pk)
        if target.is_hidden:
            raise ModerationError("This content is already hidden. Dismiss the duplicate report.")
        target.is_hidden = True
        target.save(update_fields=["is_hidden"])
        kind = ModerationAction.Kind.HIDE_POST if post else ModerationAction.Kind.HIDE_REPLY
    elif decision == "suspend":
        suspension, _created = PostingSuspension.objects.select_for_update().get_or_create(member=target_author)
        if suspension.is_suspended:
            raise ModerationError("This member is already suspended. Dismiss the duplicate report.")
        suspension.is_suspended = True
        suspension.save(update_fields=["is_suspended", "updated_at"])
        kind = ModerationAction.Kind.SUSPEND
    else:
        kind = ModerationAction.Kind.DISMISS

    report.status = DiscussionReport.Status.RESOLVED
    report.resolved_at = timezone.now()
    report.resolved_by = actor
    report.save(update_fields=["status", "resolved_at", "resolved_by"])
    return ModerationAction.objects.create(
        actor=actor, report=report, post=post if decision == "hide" else None,
        reply=reply if decision == "hide" else None,
        member=target_author if decision == "suspend" else None, kind=kind, reason=reason,
    )


@transaction.atomic
def restore_content(actor, reason, post_id=None, reply_id=None):
    require_owner(actor)
    if (post_id is None) == (reply_id is None):
        raise ModerationError("Restore exactly one item.")
    model = DiscussionPost if post_id is not None else DiscussionReply
    target = get_object_or_404(model.objects.select_for_update(), pk=post_id if post_id is not None else reply_id)
    if not target.is_hidden:
        raise ModerationError("This content is already visible.")
    target.is_hidden = False
    target.save(update_fields=["is_hidden"])
    return ModerationAction.objects.create(
        actor=actor, post=target if post_id is not None else None,
        reply=target if reply_id is not None else None,
        kind=ModerationAction.Kind.RESTORE_POST if post_id is not None else ModerationAction.Kind.RESTORE_REPLY,
        reason=reason,
    )


@transaction.atomic
def restore_member(actor, member_id, reason):
    require_owner(actor)
    suspension = get_object_or_404(PostingSuspension.objects.select_for_update(), member_id=member_id)
    if not suspension.is_suspended:
        raise ModerationError("This member can already post.")
    suspension.is_suspended = False
    suspension.save(update_fields=["is_suspended", "updated_at"])
    return ModerationAction.objects.create(
        actor=actor, member_id=member_id, kind=ModerationAction.Kind.RESTORE_MEMBER, reason=reason,
    )
