# Generated by Django 4.2.7 on 2023-11-16 15:18

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("event", "0002_event_name_eventrequest"),
    ]

    operations = [
        migrations.AddField(
            model_name="event",
            name="is_finished",
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name="event",
            name="end_date",
            field=models.DateTimeField(help_text="Y-M-D"),
        ),
        migrations.AlterField(
            model_name="event",
            name="start_date",
            field=models.DateTimeField(help_text="Y-M-D"),
        ),
    ]