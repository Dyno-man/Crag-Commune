from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from django import forms

from .models import Outing


PILOT_TIME_ZONE = ZoneInfo("America/New_York")


def parse_local_time(value):
    try:
        local = datetime.strptime(value, "%Y-%m-%dT%H:%M")
    except (TypeError, ValueError) as exc:
        raise forms.ValidationError("Enter a date and time.") from exc
    first = local.replace(tzinfo=PILOT_TIME_ZONE, fold=0)
    second = local.replace(tzinfo=PILOT_TIME_ZONE, fold=1)
    if first.utcoffset() != second.utcoffset():
        raise forms.ValidationError("This time falls during a clock change. Choose another time.")
    utc = first.astimezone(timezone.utc)
    if utc.astimezone(PILOT_TIME_ZONE).replace(tzinfo=None) != local:
        raise forms.ValidationError("This local time does not exist. Choose another time.")
    return utc


class OutingForm(forms.ModelForm):
    field_order = ("title", "description", "start_local", "end_local", "capacity", "join_policy", "private_meetup")
    start_local = forms.CharField(label="Start (Stone Fort local time)", widget=forms.DateTimeInput(attrs={"type": "datetime-local"}))
    end_local = forms.CharField(label="Approximate end (Stone Fort local time)", widget=forms.DateTimeInput(attrs={"type": "datetime-local"}))

    class Meta:
        model = Outing
        fields = ("title", "description", "capacity", "join_policy", "private_meetup")
        labels = {"private_meetup": "Meetup details (accepted members only)"}
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "private_meetup": forms.Textarea(attrs={"rows": 3}),
        }

    def clean(self):
        cleaned = super().clean()
        for key in ("start_local", "end_local"):
            if key in cleaned:
                try:
                    cleaned[key + "_utc"] = parse_local_time(cleaned[key])
                except forms.ValidationError as exc:
                    self.add_error(key, exc)
        start = cleaned.get("start_local_utc")
        end = cleaned.get("end_local_utc")
        if start and end and end <= start:
            self.add_error("end_local", "End time must be after start time.")
        return cleaned

    def save(self, commit=True):
        outing = super().save(commit=False)
        outing.starts_at = self.cleaned_data["start_local_utc"]
        outing.ends_at = self.cleaned_data["end_local_utc"]
        if commit:
            outing.save()
        return outing


class CancellationForm(forms.Form):
    note = forms.CharField(
        label="Note to accepted members (optional)",
        max_length=280,
        required=False,
        widget=forms.Textarea(attrs={"rows": 3}),
    )


class EditOutingForm(OutingForm):
    version = forms.IntegerField(widget=forms.HiddenInput(), min_value=1)
    acknowledge_change = forms.BooleanField(
        required=False,
        label="I understand accepted members will receive a notice about these changes.",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk and not self.is_bound:
            self.fields["start_local"].initial = self.instance.starts_at.astimezone(PILOT_TIME_ZONE).strftime("%Y-%m-%dT%H:%M")
            self.fields["end_local"].initial = self.instance.ends_at.astimezone(PILOT_TIME_ZONE).strftime("%Y-%m-%dT%H:%M")
            self.fields["version"].initial = self.instance.version
