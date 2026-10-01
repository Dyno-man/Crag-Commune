from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import F, Q


class Outing(models.Model):
    class JoinPolicy(models.TextChoices):
        REQUEST = "request", "Host approval"
        OPEN = "open", "Open until full"

    class Status(models.TextChoices):
        OPEN = "open", "Open"
        CANCELLED = "cancelled", "Cancelled"

    host = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="hosted_outings")
    area_name = models.CharField(max_length=80, default="Stone Fort")
    title = models.CharField(max_length=120)
    description = models.TextField(max_length=1000)
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField()
    time_zone = models.CharField(max_length=64, default="America/New_York")
    capacity = models.PositiveSmallIntegerField(default=8, help_text="Total people, including the host")
    join_policy = models.CharField(max_length=16, choices=JoinPolicy.choices, default=JoinPolicy.REQUEST)
    private_meetup = models.TextField(max_length=500, blank=True)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.OPEN)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    cancelled_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.PROTECT, related_name="cancelled_outings"
    )
    cancellation_note = models.CharField(max_length=280, blank=True)
    version = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["starts_at", "pk"]
        constraints = [
            models.CheckConstraint(condition=Q(capacity__gte=1), name="outing_capacity_positive"),
            models.CheckConstraint(condition=Q(ends_at__gt=F("starts_at")), name="outing_end_after_start"),
        ]

    def clean(self):
        if self.ends_at and self.starts_at and self.ends_at <= self.starts_at:
            raise ValidationError({"ends_at": "End time must be after start time."})

    def accepted_count(self):
        return self.participations.filter(status=Participation.Status.ACCEPTED).count()

    def spaces_left(self):
        return max(0, self.capacity - 1 - self.accepted_count())

    def can_view_private(self, user):
        return self.status == self.Status.OPEN and user.is_authenticated and (
            user.pk == self.host_id or self.participations.filter(member=user, status=Participation.Status.ACCEPTED).exists()
        )


class Participation(models.Model):
    class Status(models.TextChoices):
        REQUESTED = "requested", "Requested"
        ACCEPTED = "accepted", "Accepted"
        DECLINED = "declined", "Declined"
        WITHDRAWN = "withdrawn", "Withdrawn"
        WAITLISTED = "waitlisted", "Waitlisted"

    outing = models.ForeignKey(Outing, on_delete=models.CASCADE, related_name="participations")
    member = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="outing_participations")
    status = models.CharField(max_length=16, choices=Status.choices)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["outing", "member"], name="one_participation_per_member")]


class OutingRevision(models.Model):
    outing = models.ForeignKey(Outing, on_delete=models.CASCADE, related_name="revisions")
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="outing_revisions")
    changes = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "-pk"]


class OutingNotice(models.Model):
    class Kind(models.TextChoices):
        CANCELLED = "cancelled", "Outing cancelled"
        CHANGED = "changed", "Outing changed"

    outing = models.ForeignKey(Outing, on_delete=models.CASCADE, related_name="notices")
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="outing_notices")
    revision = models.ForeignKey(OutingRevision, null=True, blank=True, on_delete=models.CASCADE, related_name="notices")
    kind = models.CharField(max_length=16, choices=Kind.choices)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "-pk"]
        constraints = [
            models.UniqueConstraint(
                fields=["outing", "recipient"],
                condition=Q(kind="cancelled"),
                name="one_cancellation_notice_per_member",
            ),
            models.UniqueConstraint(
                fields=["revision", "recipient"],
                condition=Q(kind="changed"),
                name="one_change_notice_per_member",
            ),
        ]


class DiscussionCategory(models.Model):
    slug = models.SlugField(max_length=40, unique=True)
    name = models.CharField(max_length=80)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class DiscussionPost(models.Model):
    category = models.ForeignKey(DiscussionCategory, on_delete=models.PROTECT, related_name="posts")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="discussion_posts")
    title = models.CharField(max_length=120)
    body = models.TextField(max_length=3000)
    is_hidden = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "-pk"]


class DiscussionReply(models.Model):
    post = models.ForeignKey(DiscussionPost, on_delete=models.CASCADE, related_name="replies")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="discussion_replies")
    body = models.TextField(max_length=1500)
    is_hidden = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at", "pk"]


class DiscussionReport(models.Model):
    class Status(models.TextChoices):
        OPEN = "open", "Open"
        RESOLVED = "resolved", "Resolved"

    reporter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="discussion_reports")
    post = models.ForeignKey(DiscussionPost, on_delete=models.PROTECT, null=True, blank=True, related_name="reports")
    reply = models.ForeignKey(DiscussionReply, on_delete=models.PROTECT, null=True, blank=True, related_name="reports")
    reason = models.TextField(max_length=500)
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.OPEN)
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True, blank=True, related_name="resolved_discussion_reports"
    )

    class Meta:
        ordering = ["-created_at", "-pk"]
        constraints = [
            models.CheckConstraint(
                condition=(Q(post__isnull=False, reply__isnull=True) | Q(post__isnull=True, reply__isnull=False)),
                name="discussion_report_one_target",
            ),
            models.UniqueConstraint(
                fields=["reporter", "post"], condition=Q(post__isnull=False), name="one_report_per_member_post"
            ),
            models.UniqueConstraint(
                fields=["reporter", "reply"], condition=Q(reply__isnull=False), name="one_report_per_member_reply"
            ),
        ]


class PostingSuspension(models.Model):
    member = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="posting_suspension")
    is_suspended = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)


class ModerationAction(models.Model):
    class Kind(models.TextChoices):
        DISMISS = "dismiss", "Report dismissed"
        HIDE_POST = "hide_post", "Post hidden"
        HIDE_REPLY = "hide_reply", "Reply hidden"
        RESTORE_POST = "restore_post", "Post restored"
        RESTORE_REPLY = "restore_reply", "Reply restored"
        SUSPEND = "suspend", "Posting suspended"
        RESTORE_MEMBER = "restore_member", "Posting restored"

    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="moderation_actions")
    report = models.ForeignKey(DiscussionReport, on_delete=models.PROTECT, null=True, blank=True, related_name="actions")
    post = models.ForeignKey(DiscussionPost, on_delete=models.PROTECT, null=True, blank=True)
    reply = models.ForeignKey(DiscussionReply, on_delete=models.PROTECT, null=True, blank=True)
    member = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True, blank=True)
    kind = models.CharField(max_length=20, choices=Kind.choices)
    reason = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "-pk"]
