import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


def seed_categories(apps, schema_editor):
    category = apps.get_model("community", "DiscussionCategory")
    for slug, name in (
        ("find-partners", "Find partners"),
        ("upcoming-outings", "Upcoming outings"),
        ("local-questions", "Local questions"),
        ("access-stewardship", "Access or stewardship"),
    ):
        category.objects.create(slug=slug, name=name)


class Migration(migrations.Migration):
    dependencies = [
        ("community", "0003_outing_revisions"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="DiscussionCategory",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("slug", models.SlugField(max_length=40, unique=True)),
                ("name", models.CharField(max_length=80)),
            ],
            options={"ordering": ["name"]},
        ),
        migrations.CreateModel(
            name="DiscussionPost",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=120)),
                ("body", models.TextField(max_length=3000)),
                ("is_hidden", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("author", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="discussion_posts", to=settings.AUTH_USER_MODEL)),
                ("category", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="posts", to="community.discussioncategory")),
            ],
            options={"ordering": ["-created_at", "-pk"]},
        ),
        migrations.CreateModel(
            name="DiscussionReply",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("body", models.TextField(max_length=1500)),
                ("is_hidden", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("author", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="discussion_replies", to=settings.AUTH_USER_MODEL)),
                ("post", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="replies", to="community.discussionpost")),
            ],
            options={"ordering": ["created_at", "pk"]},
        ),
        migrations.RunPython(seed_categories, migrations.RunPython.noop),
    ]
