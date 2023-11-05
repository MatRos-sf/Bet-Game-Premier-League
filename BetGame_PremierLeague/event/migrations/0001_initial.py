# Generated by Django 4.2.6 on 2023-11-05 13:33

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Event",
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
                ("start_date", models.DateTimeField()),
                ("end_date", models.DateTimeField()),
                (
                    "description",
                    models.TextField(blank=True, max_length=300, null=True),
                ),
                ("fee", models.IntegerField(default=0)),
                (
                    "first_place",
                    models.PositiveSmallIntegerField(
                        default=60,
                        help_text="The field that specifies the percentage win for 1st place.",
                    ),
                ),
                (
                    "second_place",
                    models.PositiveSmallIntegerField(
                        default=30,
                        help_text="The field that specifies the percentage win for 2nd place.",
                    ),
                ),
                (
                    "third_place",
                    models.PositiveSmallIntegerField(
                        default=10,
                        help_text="The field that specifies the percentage win for 3rd place.",
                    ),
                ),
                (
                    "members",
                    models.ManyToManyField(
                        blank=True, related_name="events", to=settings.AUTH_USER_MODEL
                    ),
                ),
                (
                    "owner",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
