# Generated by Django 4.2.6 on 2023-11-06 13:35

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("league", "0002_alter_team_currently_league"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="season",
            name="matchweek",
        ),
    ]