# Generated by Django 4.2.7 on 2023-12-28 08:35

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0003_alter_userscores_kind"),
    ]

    operations = [
        migrations.AlterField(
            model_name="userscores",
            name="kind",
            field=models.CharField(
                choices=[("bet", "Bet"), ("event", "Event"), ("other", "Other")],
                default="bet",
                max_length=10,
            ),
        ),
    ]
