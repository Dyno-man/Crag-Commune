from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("accounts", "0002_alter_member_username")]

    operations = [
        migrations.CreateModel(
            name="AuthAttemptBucket",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("key", models.CharField(max_length=64, unique=True)),
                ("attempts", models.PositiveSmallIntegerField(default=0)),
                ("expires_at", models.DateTimeField(db_index=True)),
            ],
        ),
    ]
