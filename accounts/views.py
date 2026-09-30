from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ProfileForm, SignupForm
from .models import Member
from .rate_limits import login_retry_after, signup_retry_after


RETRY_MESSAGE = "Too many attempts. Please wait a few minutes and try again."


class LimitedLoginView(LoginView):
    template_name = "accounts/login.html"

    def post(self, request, *args, **kwargs):
        retry_after = login_retry_after(request)
        if retry_after:
            response = self.render_to_response(
                self.get_context_data(form=self.get_form_class()(request=request), rate_limit_error=RETRY_MESSAGE),
                status=429,
            )
            response["Retry-After"] = str(retry_after)
            return response
        return super().post(request, *args, **kwargs)


def signup(request):
    if request.user.is_authenticated:
        return redirect("accounts:me")
    form = SignupForm(request.POST or None)
    if request.method == "POST":
        retry_after = signup_retry_after(request)
        if retry_after:
            response = render(request, "accounts/signup.html", {"form": SignupForm(), "rate_limit_error": RETRY_MESSAGE}, status=429)
            response["Retry-After"] = str(retry_after)
            return response
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
