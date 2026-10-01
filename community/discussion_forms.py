from django import forms

from .models import DiscussionPost, DiscussionReply


class DiscussionPostForm(forms.ModelForm):
    class Meta:
        model = DiscussionPost
        fields = ("category", "title", "body")
        widgets = {"body": forms.Textarea(attrs={"rows": 8})}
        labels = {"body": "Post"}


class DiscussionReplyForm(forms.ModelForm):
    class Meta:
        model = DiscussionReply
        fields = ("body",)
        widgets = {"body": forms.Textarea(attrs={"rows": 5})}
        labels = {"body": "Reply"}


class ReportForm(forms.Form):
    reason = forms.CharField(max_length=500, widget=forms.Textarea(attrs={"rows": 3}))


class ModerationDecisionForm(forms.Form):
    decision = forms.ChoiceField(choices=(("dismiss", "Dismiss"), ("hide", "Hide content"), ("suspend", "Suspend author from posting")))
    reason = forms.CharField(max_length=500, widget=forms.Textarea(attrs={"rows": 2}))


class ModerationReasonForm(forms.Form):
    reason = forms.CharField(max_length=500)
