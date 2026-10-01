from django.conf import settings


def discussion_status(_request):
    return {"discussion_enabled": settings.DISCUSSION_ENABLED}
