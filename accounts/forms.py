from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import Member


class SignupForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = Member
        fields = ("username", "email")
        labels = {"username": "Public name", "email": "Email (private, optional)"}
        help_texts = {
            "username": "Choose a name other climbers can see. It does not need to be your real name.",
            "email": "Not shown on your profile. Email recovery is not available yet.",
        }

    def clean_username(self):
        username = self.cleaned_data["username"]
        if Member.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError("This public name is already in use.")
        return username


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Member
        fields = ("bio", "home_region")
        labels = {"bio": "About you", "home_region": "Approximate home region"}
        widgets = {"bio": forms.Textarea(attrs={"rows": 4})}
