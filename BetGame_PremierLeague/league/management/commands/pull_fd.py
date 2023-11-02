from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from league.models import Season
from football_data.premier_league import PremierLeague, Season


class Command(BaseCommand):
    help = "Hello ;) "

    def add_arguments(self, parser):
        parser.add_argument(
            "--season", type=int, default=timezone.now().date().year, nargs="?"
        )

    def handle(self, *args, **options):
        # season = options['season']

        pl = PremierLeague()
        pl.pull()

        # league
        league = ...
        # get season
        season = self.capture_or_create_season(league, pl.season)

    def capture_or_create_season(self, league, season: Season) -> Season:
        try:
            season = Season.objects.get(fb_id=instance.season.fb_id)
        except Season.DoesNotExist:
            self.stdout.write(
                f"Season {season} doesn't exist!\nI'm creating new season.", ending="\n"
            )
            season = Season.objects.create(**instance.season.__dict__, league=league)
            self.stdout.write(f"Season {season} has been created!", ending="\n")

        return season
