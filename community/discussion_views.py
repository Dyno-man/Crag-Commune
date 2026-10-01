from functools import wraps

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods, require_POST

from .discussion_forms import DiscussionPostForm, DiscussionReplyForm, ModerationDecisionForm, ModerationReasonForm, ReportForm
from .models import DiscussionCategory, DiscussionPost, DiscussionReply, DiscussionReport, ModerationAction, PostingSuspension
from .moderation import ModerationError, can_post, decide_report, require_owner, restore_content, restore_member, submit_report


def discussion_open(view):
    @wraps(view)
    def guarded(request, *args, **kwargs):
        if not settings.DISCUSSION_ENABLED:
            raise Http404("Discussion is not open yet.")
        return view(request, *args, **kwargs)

    return guarded


@discussion_open
def index(request):
    categories = DiscussionCategory.objects.all()
    selected = request.GET.get("category", "")
    query = request.GET.get("q", "").strip()[:100]
    posts = DiscussionPost.objects.filter(is_hidden=False).select_related("author", "category")
    if selected:
        get_object_or_404(categories, slug=selected)
        posts = posts.filter(category__slug=selected)
    if query:
        posts = posts.filter(Q(title__icontains=query) | Q(body__icontains=query))
    return render(request, "community/discussion_index.html", {
        "categories": categories,
        "selected": selected,
        "query": query,
        "posts": posts[:50],
        "can_post": can_post(request.user),
    })


@discussion_open
@login_required
@require_http_methods(["GET", "POST"])
def create(request):
    if not can_post(request.user):
        raise PermissionDenied("Posting is suspended.")
    form = DiscussionPostForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect("discussion:detail", pk=post.pk)
    return render(request, "community/discussion_form.html", {"form": form})


@discussion_open
def detail(request, pk):
    post = get_object_or_404(DiscussionPost.objects.filter(is_hidden=False).select_related("author", "category"), pk=pk)
    replies = post.replies.filter(is_hidden=False).select_related("author")
    return render(request, "community/discussion_detail.html", {
        "post": post, "replies": replies, "reply_form": DiscussionReplyForm(), "can_post": can_post(request.user),
    })


@discussion_open
@login_required
@require_POST
def reply(request, pk):
    if not can_post(request.user):
        raise PermissionDenied("Posting is suspended.")
    post = get_object_or_404(DiscussionPost.objects.filter(is_hidden=False), pk=pk)
    form = DiscussionReplyForm(request.POST)
    if form.is_valid():
        response = form.save(commit=False)
        response.post = post
        response.author = request.user
        response.save()
        return redirect("discussion:detail", pk=post.pk)
    return render(request, "community/discussion_detail.html", {
        "post": post, "replies": post.replies.filter(is_hidden=False).select_related("author"),
        "reply_form": form, "can_post": True,
    }, status=400)


@discussion_open
@login_required
@require_POST
def report_post(request, pk):
    form = ReportForm(request.POST)
    if form.is_valid():
        try:
            submit_report(request.user, form.cleaned_data["reason"], post_id=pk)
        except ModerationError as exc:
            raise PermissionDenied(str(exc)) from exc
        messages.success(request, "Report sent to the site owner.")
        return redirect("discussion:detail", pk=pk)
    return render(request, "community/discussion_report_error.html", {"form": form}, status=400)


@discussion_open
@login_required
@require_POST
def report_reply(request, pk, reply_id):
    reply = get_object_or_404(DiscussionReply.objects.filter(post_id=pk), pk=reply_id)
    form = ReportForm(request.POST)
    if form.is_valid():
        try:
            submit_report(request.user, form.cleaned_data["reason"], reply_id=reply.pk)
        except ModerationError as exc:
            raise PermissionDenied(str(exc)) from exc
        messages.success(request, "Report sent to the site owner.")
        return redirect("discussion:detail", pk=pk)
    return render(request, "community/discussion_report_error.html", {"form": form}, status=400)


@discussion_open
@login_required
def moderation_index(request):
    require_owner(request.user)
    return render(request, "community/discussion_moderation.html", {
        "reports": DiscussionReport.objects.filter(status=DiscussionReport.Status.OPEN).select_related(
            "reporter", "post__author", "reply__author", "reply__post"
        )[:50],
        "hidden_posts": DiscussionPost.objects.filter(is_hidden=True).select_related("author")[:25],
        "hidden_replies": DiscussionReply.objects.filter(is_hidden=True).select_related("author", "post")[:25],
        "suspensions": PostingSuspension.objects.filter(is_suspended=True).select_related("member")[:25],
        "actions": ModerationAction.objects.select_related("actor")[:25],
    })


@discussion_open
@login_required
@require_POST
def moderate_report(request, report_id):
    require_owner(request.user)
    form = ModerationDecisionForm(request.POST)
    if not form.is_valid():
        return render(request, "community/discussion_report_error.html", {"form": form}, status=400)
    try:
        decide_report(report_id, request.user, form.cleaned_data["decision"], form.cleaned_data["reason"])
    except ModerationError as exc:
        messages.error(request, str(exc))
    else:
        messages.success(request, "Report handled and action recorded.")
    return redirect("discussion:moderation")


@discussion_open
@login_required
@require_POST
def restore_post(request, pk):
    return restore_content_view(request, post_id=pk)


@discussion_open
@login_required
@require_POST
def restore_reply(request, reply_id):
    return restore_content_view(request, reply_id=reply_id)


def restore_content_view(request, post_id=None, reply_id=None):
    require_owner(request.user)
    form = ModerationReasonForm(request.POST)
    if not form.is_valid():
        return render(request, "community/discussion_report_error.html", {"form": form}, status=400)
    try:
        restore_content(request.user, form.cleaned_data["reason"], post_id=post_id, reply_id=reply_id)
    except ModerationError as exc:
        messages.error(request, str(exc))
    else:
        messages.success(request, "Content restored and action recorded.")
    return redirect("discussion:moderation")


@discussion_open
@login_required
@require_POST
def restore_account(request, member_id):
    require_owner(request.user)
    form = ModerationReasonForm(request.POST)
    if not form.is_valid():
        return render(request, "community/discussion_report_error.html", {"form": form}, status=400)
    try:
        restore_member(request.user, member_id, form.cleaned_data["reason"])
    except ModerationError as exc:
        messages.error(request, str(exc))
    else:
        messages.success(request, "Posting restored and action recorded.")
    return redirect("discussion:moderation")
