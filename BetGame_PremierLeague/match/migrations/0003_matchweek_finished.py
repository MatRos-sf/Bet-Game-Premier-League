# Generated by Django 4.2.6 on 2023-10-27 17:44

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("match", "0002_alter_match_matchweek"),
    ]

    operations = [
        migrations.AddField(
            model_name="matchweek",
            name="finished",
            field=models.BooleanField(default=False),
        ),
    ]