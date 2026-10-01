from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_POST

from accounts.models import Member

from .blocks import block_member, unblock_member


@login_required
@require_POST
def block(request, username):
    target = get_object_or_404(Member, username__iexact=username, is_active=True)
    if target.pk == request.user.pk:
        return redirect("accounts:public_profile", username=target.username)
    block_member(request.user, target)
    return redirect("accounts:public_profile", username=target.username)


@login_required
@require_POST
def unblock(request, username):
    target = get_object_or_404(Member, username__iexact=username, is_active=True)
    unblock_member(request.user, target)
    return redirect("accounts:public_profile", username=target.username)
