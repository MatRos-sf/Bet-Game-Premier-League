from django.core.management.base import BaseCommand
from django_q.models import Schedule


class Command(BaseCommand):
    help = "Execute the command to set workers."

    def handle(self, *args, **options):
        Schedule.objects.create(
            name="dashboard",
            func="cron.func.check_and_update_currently_matchweek",
            hook="cron.hooks.check_and_update_currently_matchweek_info",
            schedule_type=Schedule.HOURLY,
            repeats=-1,
        )
        self.stdout.write("First task has been created.", ending="+ \n")
        Schedule.objects.create(
            name="event_update",
            func="cron.func_event.check_event",
            hook="cron.hooks.check_event_info",
            schedule_type=Schedule.DAILY,
            repeats=-1,
        )
        self.stdout.write("Second task has been created.", ending="+ \n")
        Schedule.objects.create(
            name="cancelled_matches_update",
            func="cron.func.check_and_update_cancelled_matches",
            hook="cron.hooks.check_match",
            schedule_type=Schedule.DAILY,
            repeats=-1,
        )
        self.stdout.write("Third task has been created.", ending="+ \n")
