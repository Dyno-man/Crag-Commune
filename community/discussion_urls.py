from django.urls import path

from . import discussion_views

app_name = "discussion"

urlpatterns = [
    path("", discussion_views.index, name="index"),
    path("new/", discussion_views.create, name="create"),
    path("<int:pk>/", discussion_views.detail, name="detail"),
    path("<int:pk>/reply/", discussion_views.reply, name="reply"),
]
