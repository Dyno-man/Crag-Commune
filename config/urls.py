from django.http import JsonResponse
from django.shortcuts import render
from django.urls import include, path


def health(_request):
    return JsonResponse({"status": "ok"})


def home(request):
    return render(request, "home.html")


urlpatterns = [
    path("", home, name="home"),
    path("health/", health, name="health"),
    path("accounts/", include("accounts.urls")),
]
