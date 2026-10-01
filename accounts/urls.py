from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("join/", views.signup, name="signup"),
    path("login/", views.LimitedLoginView.as_view(), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("me/", views.me, name="me"),
    path("members/<str:username>/", views.public_profile, name="public_profile"),
]
