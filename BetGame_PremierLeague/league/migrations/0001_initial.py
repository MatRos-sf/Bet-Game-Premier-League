# Generated by Django 4.2.6 on 2023-10-24 10:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="League",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100, unique=True)),
                ("country", models.CharField(max_length=50)),
                ("emblem", models.URLField(blank=True, null=True)),
                ("last_modified", models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name="Season",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "fb_id",
                    models.CharField(
                        help_text="Season id from football database.",
                        max_length=20,
                        unique=True,
                    ),
                ),
                ("start_date", models.DateField()),
                ("end_date", models.DateField()),
                ("matchweek", models.PositiveIntegerField(default=1)),
                ("is_currently", models.BooleanField(default=True)),
                (
                    "league",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="league.league"
                    ),
                ),
            ],
            options={
                "ordering": ["start_date"],
            },
        ),
        migrations.CreateModel(
            name="Team",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("fb_id", models.CharField(max_length=20, unique=True)),
                ("name", models.CharField(max_length=100)),
                ("short_name", models.CharField(blank=True, max_length=50, null=True)),
                ("shortcut", models.CharField(blank=True, max_length=5, null=True)),
                ("crest", models.URLField(blank=True, null=True)),
                ("website", models.URLField(blank=True, null=True)),
                (
                    "club_colours",
                    models.CharField(blank=True, max_length=150, null=True),
                ),
                (
                    "currently_league",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="teams",
                        to="league.league",
                    ),
                ),
                (
                    "last_league",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="previous_season_teams",
                        to="league.league",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="TeamStats",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("played", models.SmallIntegerField(default=0)),
                ("won", models.SmallIntegerField(default=0)),
                ("drawn", models.SmallIntegerField(default=0)),
                ("lost", models.SmallIntegerField(default=0)),
                ("goals_for", models.SmallIntegerField(default=0)),
                ("goals_against", models.SmallIntegerField(default=0)),
                ("points", models.SmallIntegerField(default=0)),
                (
                    "season",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="league.season"
                    ),
                ),
                (
                    "team",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="stats",
                        to="league.team",
                    ),
                ),
            ],
        ),
    ]
