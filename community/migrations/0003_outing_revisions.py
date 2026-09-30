import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("community", "0002_outing_cancellation_notices"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="outing",
            name="version",
            field=models.PositiveIntegerField(default=1),
        ),
        migrations.CreateModel(
            name="OutingRevision",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("changes", models.JSONField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("changed_by", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="outing_revisions", to=settings.AUTH_USER_MODEL)),
                ("outing", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="revisions", to="community.outing")),
            ],
            options={"ordering": ["-created_at", "-pk"]},
        ),
        migrations.AddField(
            model_name="outingnotice",
            name="revision",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name="notices", to="community.outingrevision"),
        ),
        migrations.AlterField(
            model_name="outingnotice",
            name="kind",
            field=models.CharField(choices=[("cancelled", "Outing cancelled"), ("changed", "Outing changed")], max_length=16),
        ),
        migrations.AddConstraint(
            model_name="outingnotice",
            constraint=models.UniqueConstraint(condition=models.Q(("kind", "changed")), fields=("revision", "recipient"), name="one_change_notice_per_member"),
        ),
    ]
