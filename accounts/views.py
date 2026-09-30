from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ProfileForm, SignupForm
from .models import Member


def signup(request):
    if request.user.is_authenticated:
        return redirect("accounts:me")
    form = SignupForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        member = form.save()
        login(request, member)
        return redirect("accounts:me")
    return render(request, "accounts/signup.html", {"form": form})


@login_required
def me(request):
    form = ProfileForm(request.POST or None, instance=request.user)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("accounts:me")
    return render(request, "accounts/me.html", {"form": form})


def public_profile(request, username):
    member = get_object_or_404(Member, username__iexact=username, is_active=True)
    return render(request, "accounts/public_profile.html", {"member": member})
