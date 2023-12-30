import random
from typing import List

from bet.models import Bet
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from faker import Faker
from match.models import Match


class Simulation:
    def __init__(self):
        self.users: List[User] = []
        self.fake = Faker()
        self.top_clubs = [
            "Chelsea FC",
            "Arsenal FC",
            "Liverpool FC",
            "Manchester City FC",
            "Manchester United FC",
        ]
        self.options = ["home", "draw", "away"]

    def create_user(self, amt: int = 10):
        for _ in range(amt):
            user = User.objects.create_user(self.fake.user_name(), password="admin1")
            self.users.append(user)

        print("Users has been created!")

    def choice(self, home_team: str, away_team: str) -> str:
        if home_team in self.top_clubs and away_team not in self.top_clubs:
            return random.choices(self.options, [0.6, 0.20, 0.20])[0]
        elif home_team not in self.top_clubs and away_team in self.top_clubs:
            return random.choices(self.options, [0.20, 0.20, 0.6])[0]
        return random.choice(self.options)

    def bet_match(self):
        for match in Match.objects.all():
            if not match.finished:
                continue

            for user in self.users:
                bet_or_not = random.choices([True, False], [0.9, 0.1])[0]

                if bet_or_not:
                    user_choice = self.choice(match.home_team, match.away_team)
                    risk_or_not = random.choice([True, False])
                    if risk_or_not and user.profile.all_points > 1:
                        bet = Bet.objects.create(
                            match=match, user=user, choice=user_choice, risk=True
                        )
                    else:
                        bet = Bet.objects.create(
                            match=match, user=user, choice=user_choice, risk=False
                        )
                    bet.check_bet()


class Command(BaseCommand):
    def handle(self, *args, **options):
        simulation = Simulation()

        simulation.create_user()
        self.stdout.write("Created users!")
        simulation.bet_match()
        self.stdout.write("Created bets!")
