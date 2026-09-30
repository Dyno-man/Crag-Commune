from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_http_methods, require_POST

from .forms import CancellationForm, OutingForm
from .models import Outing, OutingNotice, Participation
from .services import ParticipationError, cancel_outing, host_decide, request_to_join, withdraw


def outing_list(request):
    outings = Outing.objects.filter(status=Outing.Status.OPEN, ends_at__gte=timezone.now()).select_related("host")
    with timezone.override("America/New_York"):
        return render(request, "community/list.html", {"outings": outings})


@login_required
def outing_create(request):
    form = OutingForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        outing = form.save(commit=False)
        outing.host = request.user
        outing.save()
        return redirect("community:detail", pk=outing.pk)
    return render(request, "community/create.html", {"form": form})


def outing_detail(request, pk):
    outing = get_object_or_404(Outing.objects.select_related("host"), pk=pk)
    can_view_private = outing.can_view_private(request.user)
    my_participation = None
    if request.user.is_authenticated:
        my_participation = outing.participations.filter(member=request.user).first()
    can_view_cancellation_note = request.user.is_authenticated and (
        request.user.pk == outing.host_id
        or OutingNotice.objects.filter(outing=outing, recipient=request.user, kind=OutingNotice.Kind.CANCELLED).exists()
    )
    participants = outing.participations.filter(status=Participation.Status.ACCEPTED).select_related("member") if can_view_private else None
    requests = outing.participations.filter(status__in=[Participation.Status.REQUESTED, Participation.Status.WAITLISTED]).select_related("member") if outing.status == Outing.Status.OPEN and request.user.is_authenticated and request.user.pk == outing.host_id else None
    with timezone.override(outing.time_zone):
        return render(request, "community/detail.html", {
            "outing": outing,
            "can_view_private": can_view_private,
            "my_participation": my_participation,
            "participants": participants,
            "requests": requests,
            "can_view_cancellation_note": can_view_cancellation_note,
        })


@login_required
def outing_notices(request):
    notices = OutingNotice.objects.filter(recipient=request.user).select_related("outing")[:50]
    with timezone.override("America/New_York"):
        return render(request, "community/notices.html", {"notices": notices})


@login_required
@require_http_methods(["GET", "POST"])
def cancel(request, pk):
    outing = get_object_or_404(Outing, pk=pk)
    if outing.host_id != request.user.pk:
        raise PermissionDenied("Only the host can cancel this outing.")
    if outing.status == Outing.Status.CANCELLED:
        return redirect("community:detail", pk=pk)
    form = CancellationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        cancel_outing(pk, request.user, form.cleaned_data["note"])
        messages.success(request, "Outing cancelled. Accepted members can see the notice in-app.")
        return redirect("community:detail", pk=pk)
    return render(request, "community/cancel.html", {"outing": outing, "form": form})


@login_required
@require_POST
def join(request, pk):
    get_object_or_404(Outing, pk=pk)
    try:
        participation = request_to_join(pk, request.user)
        messages.success(request, f"Your status is {participation.get_status_display().lower()}.")
    except ParticipationError as exc:
        messages.error(request, str(exc))
    return redirect("community:detail", pk=pk)


@login_required
@require_POST
def leave(request, pk):
    get_object_or_404(Outing, pk=pk)
    try:
        withdraw(pk, request.user)
        messages.success(request, "You left this outing.")
    except Participation.DoesNotExist as exc:
        raise Http404 from exc
    return redirect("community:detail", pk=pk)


def decide(request, pk, participation_id, accept_request):
    get_object_or_404(Outing, pk=pk)
    try:
        host_decide(pk, participation_id, request.user, accept_request)
        messages.success(request, "Join request updated.")
    except Participation.DoesNotExist as exc:
        raise Http404 from exc
    except ParticipationError as exc:
        messages.error(request, str(exc))
    return redirect("community:detail", pk=pk)


@login_required
@require_POST
def accept(request, pk, participation_id):
    return decide(request, pk, participation_id, True)


@login_required
@require_POST
def decline(request, pk, participation_id):
    return decide(request, pk, participation_id, False)
