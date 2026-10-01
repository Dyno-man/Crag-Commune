from django.core.validators import RegexValidator
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="member",
            name="username",
            field=models.CharField(
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
            ),
        ),
    ]
