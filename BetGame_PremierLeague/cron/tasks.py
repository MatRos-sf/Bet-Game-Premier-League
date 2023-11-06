from django_q.models import Schedule

Schedule.objects.create(
    name="dashboard",
    func="cron.func.dashboard",
    hook="cron.hooks.dashboard_info",
    schedule_type=Schedule.HOURLY,
    repeats=-1,
)
