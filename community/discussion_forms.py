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
