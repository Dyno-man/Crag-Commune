from functools import wraps

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods, require_POST

from .discussion_forms import DiscussionPostForm, DiscussionReplyForm
from .models import DiscussionCategory, DiscussionPost


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
    })


@discussion_open
@login_required
@require_http_methods(["GET", "POST"])
def create(request):
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
        "post": post, "replies": replies, "reply_form": DiscussionReplyForm(),
    })


@discussion_open
@login_required
@require_POST
def reply(request, pk):
    post = get_object_or_404(DiscussionPost.objects.filter(is_hidden=False), pk=pk)
    form = DiscussionReplyForm(request.POST)
    if form.is_valid():
        response = form.save(commit=False)
        response.post = post
        response.author = request.user
        response.save()
        return redirect("discussion:detail", pk=post.pk)
    return render(request, "community/discussion_detail.html", {
        "post": post, "replies": post.replies.filter(is_hidden=False).select_related("author"), "reply_form": form,
    }, status=400)
