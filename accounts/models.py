from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.functions import Lower


class Member(AbstractUser):
    # Public usernames are pseudonyms. Real-name fields are intentionally absent.
    first_name = None
    last_name = None
    bio = models.CharField(max_length=280, blank=True)
    home_region = models.CharField(max_length=80, blank=True)
    REQUIRED_FIELDS = []

    class Meta:
        constraints = [
            models.UniqueConstraint(Lower("username"), name="member_username_case_insensitive_unique"),
        ]

    def __str__(self):
        return self.username
