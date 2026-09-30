from django.urls import path

from . import views

app_name = "community"

urlpatterns = [
    path("", views.outing_list, name="list"),
    path("new/", views.outing_create, name="create"),
    path("notices/", views.outing_notices, name="notices"),
    path("<int:pk>/", views.outing_detail, name="detail"),
    path("<int:pk>/edit/", views.edit, name="edit"),
    path("<int:pk>/cancel/", views.cancel, name="cancel"),
    path("<int:pk>/join/", views.join, name="join"),
    path("<int:pk>/withdraw/", views.leave, name="withdraw"),
    path("<int:pk>/requests/<int:participation_id>/accept/", views.accept, name="accept"),
    path("<int:pk>/requests/<int:participation_id>/decline/", views.decline, name="decline"),
]
