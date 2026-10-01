from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("accounts", "0003_auth_attempt_bucket")]

    operations = [
        migrations.AddField(
            model_name="member",
            name="age_eligible_confirmed_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
