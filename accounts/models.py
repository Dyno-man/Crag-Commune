from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models
from django.db.models.functions import Lower


class Member(AbstractUser):
    # Public usernames are pseudonyms. Real-name fields are intentionally absent.
    username = models.CharField(
        "username",
        max_length=150,
        unique=True,
        help_text="Required. 150 characters or fewer. Letters, digits, spaces and @/./+/-/_ only.",
        validators=[
            RegexValidator(
                regex=r"^[\w.@+-]+(?: [\w.@+-]+)*\Z",
                message="Use letters, digits, @/./+/-/_ and single spaces between words.",
            )
        ],
        error_messages={"unique": "A user with that username already exists."},
    )
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


class AuthAttemptBucket(models.Model):
    # Keys are HMACs of an address or login name; raw values are not retained.
    key = models.CharField(max_length=64, unique=True)
    attempts = models.PositiveSmallIntegerField(default=0)
    expires_at = models.DateTimeField(db_index=True)
