from unittest import mock
import plotly.graph_objects as go

from django.test import tag, TestCase
from django.contrib.auth.models import User
from django.urls import reverse

from bet.views import Chart
from league.tests.test_models import SimpleDB
from league.forms import ChoseSeasonForm
from bet.models import Bet


class UserFinishedBetsListViewTest(SimpleDB):
    def setUp(self):
        self.url = "bet-finished"
        self.sample_user = User.objects.first()

    def test_should_redirect_when_user_is_not_authenticated(self):
        response = self.client.get(reverse(self.url), follow=True)
        self.assertRedirects(response, f"/login/?next={reverse(self.url)}")

    def test_should_return_3_bets(self):
        self.client.login(username=self.sample_user.username, password="1_test_TEST_!")
        response = self.client.get(reverse(self.url), follow=True)

        context = response.context["object_list"]
        self.assertEquals(len(context), 3)


@tag("bet_view")
class BetsListViewWhenMatchweekStartTest(SimpleDB):
    def setUp(self):
        self.url = "bet-home"
        self.sample_user = User.objects.first()

    def test_should_redirect_when_user_is_not_authenticated(self):
        response = self.client.get(reverse(self.url), follow=True)
        self.assertRedirects(response, f"/login/?next={reverse(self.url)}")

    def test_should_return_appropriate_context(self):
        self.client.login(username=self.sample_user.username, password="1_test_TEST_!")
        response = self.client.get(reverse(self.url))

        context = response.context

        self.assertEquals(context["matches"].count(), 2)
        self.assertEquals(context["matchweek"].matchweek, 4)
        self.assertFalse(context["finished_matches"])

    @mock.patch("match.models.Matchweek.objects")
    def test_should_have_end_season_in_the_context(self, mock_matchweek):
        self.client.login(username=self.sample_user.username, password="1_test_TEST_!")
        mock_matchweek.filter.return_value.first.return_value = None
        response = self.client.get(reverse(self.url))

        self.assertTrue(response.context["end_season"])


@tag("chart")
class ChartTest(TestCase):
    def setUp(self):
        self.labels = ["test1", "test2", "test3"]
        self.values = [1, 2, 3]

    def test_should_set_figure_layout(self):
        chart = Chart()
        self.assertTrue(chart.figure_layout)

    def test_should_set_new_figure_layout_when_user_wants_add_new_attrs(self):
        new_attrs = {"test1": True, "test2": False}

        chart = Chart()
        chart.figure_layout = new_attrs

        # check deefault key
        self.assertEquals(chart.figure_layout.get("plot_bgcolor"), "rgba(0,0,0,0)")

        self.assertTrue(chart.figure_layout.get("test1"))
        self.assertFalse(chart.figure_layout.get("test2"))

    def test_should_override_new_figure_layout(self):
        new_layout = {"showlegend": True}

        chart = Chart()
        chart.figure_layout = new_layout

        self.assertTrue(chart.figure_layout.get("showlegend"))

    def test_create_pie_chart_default_return_type_is_figure(self):
        chart = Chart()

        expected = chart.create_pie_chart(self.labels, self.values)

        self.assertIsInstance(expected, go.Figure)

    def test_create_pie_chart_returns_str_when_requested(self):
        chart = Chart()

        expected = chart.create_pie_chart(self.labels, self.values, True)

        self.assertIsInstance(expected, str)

    def test_create_bar_chart_default_return_type_is_figure(self):
        chart = Chart()

        expected = chart.create_bar_chart(self.labels, self.values)

        self.assertIsInstance(expected, go.Figure)

    def test_create_bar_chart_returns_str_when_requested(self):
        chart = Chart()

        expected = chart.create_bar_chart(self.labels, self.values, True)

        self.assertIsInstance(expected, str)


@tag("bet_season_summary")
class BetSeasonSummaryView(SimpleDB):
    def setUp(self):
        self.url = "bet-season-summary"
        self.sample_user = User.objects.first()

    def test_should_redirect_when_user_is_not_authenticated(self):
        response = self.client.get(reverse(self.url), follow=True)
        self.assertRedirects(response, f"/login/?next={reverse(self.url)}")

    def test_return_appropriate_context_data(self):
        self.client.login(username=self.sample_user.username, password="1_test_TEST_!")
        response = self.client.get(reverse(self.url))

        context = response.context

        self.assertIsInstance(context["form"], ChoseSeasonForm)
        self.assertIsNone(context.get("season"))
        self.assertTrue(context.get("chart_kind_of_bets"))
        self.assertTrue(context.get("chart_won_lost"))
        self.assertTrue(context.get("chart_choice"))
        self.assertTrue(context.get("chart_group"))

    @mock.patch.object(Bet.objects, "filter")
    def test_context_data_should_not_contain_any_charts(self, mocked_bet):
        mocked_bet.return_value = Bet.objects.none()
        self.client.login(username=self.sample_user.username, password="1_test_TEST_!")
        response = self.client.get(reverse(self.url))

        context = response.context

        self.assertFalse(context.get("chart_won_lost", False))
        self.assertFalse(context.get("chart_choice", False))
        self.assertFalse(context.get("chart_kind_of_bets", False))
        self.assertFalse(context.get("chart_group", False))

    def test_should_return_empty_qs_when_user_use_filter(self):
        fake_season = 1
        self.client.login(username=self.sample_user.username, password="1_test_TEST_!")
        response = self.client.get(reverse(self.url) + f"?season={fake_season}")

        context = response.context

        self.assertFalse(context.get("object_list"))
        self.assertTrue(context.get("season"), fake_season)
