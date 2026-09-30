import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("community", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="outing",
            name="cancelled_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="outing",
            name="cancelled_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="cancelled_outings",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="outing",
            name="cancellation_note",
            field=models.CharField(blank=True, max_length=280),
        ),
        migrations.CreateModel(
            name="OutingNotice",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("kind", models.CharField(choices=[("cancelled", "Outing cancelled")], max_length=16)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("outing", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="notices", to="community.outing")),
                ("recipient", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="outing_notices", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "ordering": ["-created_at", "-pk"],
            },
        ),
        migrations.AddConstraint(
            model_name="outingnotice",
            constraint=models.UniqueConstraint(
                condition=models.Q(("kind", "cancelled")),
                fields=("outing", "recipient"),
                name="one_cancellation_notice_per_member",
            ),
        ),
    ]
