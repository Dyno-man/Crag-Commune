from django.urls import path

from . import discussion_views

app_name = "discussion"

urlpatterns = [
    path("", discussion_views.index, name="index"),
    path("new/", discussion_views.create, name="create"),
    path("<int:pk>/", discussion_views.detail, name="detail"),
    path("<int:pk>/reply/", discussion_views.reply, name="reply"),
    path("<int:pk>/report/", discussion_views.report_post, name="report_post"),
    path("<int:pk>/replies/<int:reply_id>/report/", discussion_views.report_reply, name="report_reply"),
    path("moderation/", discussion_views.moderation_index, name="moderation"),
    path("moderation/reports/<int:report_id>/decide/", discussion_views.moderate_report, name="moderate_report"),
    path("moderation/posts/<int:pk>/restore/", discussion_views.restore_post, name="restore_post"),
    path("moderation/replies/<int:reply_id>/restore/", discussion_views.restore_reply, name="restore_reply"),
    path("moderation/members/<int:member_id>/restore/", discussion_views.restore_account, name="restore_account"),
]
