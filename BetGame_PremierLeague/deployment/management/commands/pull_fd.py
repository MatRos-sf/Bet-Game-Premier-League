from typing import List

from django.core.management.base import BaseCommand
from football_data import premier_league as pl
from league.models import League, Season, Team, TeamStats
from match.models import Match, Matchweek


class Command(BaseCommand):
    help = (
        "Execute the command to fetch the dataset and set or update the current season."
    )

    def handle(self, *args, **options):
        """
        Main process for capturing information about the previous season,
        creating/updating league, season, teams, matchweeks, matches, and standings.

        This command should be executed before running the server to ensure that all necessary data is set up.
        """
        dataset_pl = pl.PremierLeague()
        dataset_pl.pull()

        league = self.capture_or_create_league(dataset_pl.league)
        season = self.capture_or_create_season(league, dataset_pl.season)
        self.capture_or_create_teams(league, dataset_pl.teams)
        self.capture_or_create_matchweeks_and_matches(season, dataset_pl.matchweek)
        self.capture_or_create_standings(season, dataset_pl.standings)

    def __communication_about_created(self, created: bool, communication: str) -> None:
        """
        Shows information about creating or checking the existence of a model.
        """
        if created:
            self.stdout.write(f"{communication} has been created.", ending="+ \n")
        else:
            self.stdout.write(f"{communication} exists.", ending="\u2713 \n")

    def __set_attr(self, instance, dataset: dict):
        """
        Updates or assigns new values to fields.
        """
        for field, value in dataset.items():
            if hasattr(instance, field):
                setattr(instance, field, value)
        instance.save()

    def capture_or_create_league(self, league: pl.League) -> League:
        """
        Creates or updates a league based on the provided information
        """
        league_obj, created = League.objects.get_or_create(name=league.name)
        self.__communication_about_created(created, f"The League: {league.name}")

        self.__set_attr(league_obj, league.__dict__)
        # check update

        return league_obj

    def capture_or_create_season(self, league, season: pl.Season) -> Season:
        """
        Creates or updates a season based on the provided information
        """
        season_obj, created = Season.objects.get_or_create(
            fb_id=season.fb_id, league=league
        )
        self.__communication_about_created(created, f"The season: {season.fb_id}")

        season = season.__dict__
        season["league"] = league
        self.__set_attr(season_obj, season)

        return season_obj

    def capture_or_create_teams(
        self, league: League, teams: List[pl.Team]
    ) -> List[Team]:
        """
        Creates or updates a teams based on the provided information
        """
        list_of_teams = list()

        for team in teams:
            team_obj, created = Team.objects.get_or_create(fb_id=team.fb_id)
            self.__communication_about_created(created, f"\nThe team: {team.name}")

            team = team.__dict__
            team["currently_league"] = league

            self.__set_attr(team_obj, team)
            list_of_teams.append(team_obj)

        return list_of_teams

    def capture_or_create_matchweeks_and_matches(
        self, season: Season, matchweeks: List[pl.Matchweek]
    ) -> None:
        """
        Creates or updates a matchweeks based on the provided information, including of all matches.
        """

        for matchweek in matchweeks:
            matchweek_obj, created = Matchweek.objects.get_or_create(
                season=season,
                matchweek=matchweek.matchweek,
                start_date=matchweek.start_date,
                end_date=matchweek.end_date,
            )
            self.__communication_about_created(
                created, f"The matchweek: {matchweek.matchweek}"
            )

            matches = matchweek.matches
            matchweek = matchweek.__dict__

            del (
                matchweek["matchweek"],
                matchweek["matches"],
                matchweek["season"],
                matchweek["start_date"],
                matchweek["end_date"],
            )

            self.__set_attr(matchweek_obj, matchweek)

            for match in matches:
                home_team = Team.objects.get(fb_id=match.home_team_id)
                away_team = Team.objects.get(fb_id=match.away_team_id)

                match_obj, created = Match.objects.get_or_create(
                    matchweek=matchweek_obj,
                    home_team=home_team,
                    away_team=away_team,
                    start_date=match.start_date,
                )
                self.__communication_about_created(created, f"\tThe match: {match_obj}")

                match = match.__dict__
                del (
                    match["matchweek"],
                    match["start_date"],
                    match["home_team_id"],
                    match["away_team_id"],
                )

                self.__set_attr(match_obj, match)

    def capture_or_create_standings(self, season: Season, standings):
        """
        Creates or updates a standings based on the provided information.
        """
        for s in standings:
            team = Team.objects.get(fb_id=s.team_fb_id)
            team_stats_obj, created = TeamStats.objects.get_or_create(
                team=team, season=season
            )
            self.__communication_about_created(
                created, f"Stats: {team_stats_obj.team.name}"
            )

            stats = s.__dict__
            del stats["team_fb_id"]

            self.__set_attr(team_stats_obj, stats)
