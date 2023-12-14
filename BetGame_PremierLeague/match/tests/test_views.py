from django.contrib.auth.models import User
from http import HTTPStatus
from parameterized import parameterized

from league.tests.test_models import SimpleDB
from match.models import Match


class MatchDetailViewTest(SimpleDB):
    def setUp(self):
        self.name = "match:detail"
        self.url = lambda x: f"/match/{x}/"

        self.sample_user = User.objects.first()

    @parameterized.expand([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])
    def test_view_url_does_not_exist_when_user_is_not_authenticated(self, pk):
        response = self.client.get(self.url(pk))
        self.assertRedirects(response, f"/login/?next={self.url(pk)}")

    @parameterized.expand([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11])
    def test_view_url_exist_at_desired_location_when_user_is_authenticated(self, index):
        self.client.login(username=self.sample_user.username, password="1_test_TEST_!")
        instance = self.__get_match_by_index(index)
        response = self.client.get(self.url(instance.pk))

        self.assertEquals(response.status_code, HTTPStatus.OK)

    def __get_match_by_index(self, index):
        return Match.objects.all()[index]


class ResultsSeasonListViewTest(SimpleDB):
    def setUp(self):
        self.name = "match:results"
        self.url = "/match/results/"

        self.sample_user = User.objects.first()

    def test_view_url_does_not_exist_when_user_is_not_authenticated(self):
        response = self.client.get(self.url)

        self.assertRedirects(response, f"/login/?next={self.url}")

    def test_view_url_exist_at_desired_location_when_user_is_authenticated(
        self,
    ):
        self.client.login(username=self.sample_user.username, password="1_test_TEST_!")

        response = self.client.get(self.url)
        self.assertEquals(response.status_code, HTTPStatus.OK)

    def test_should_return_six_matches(
        self,
    ):
        self.client.login(username=self.sample_user.username, password="1_test_TEST_!")

        response = self.client.get(self.url)
        object_list = response.context["object_list"]
        self.assertEquals(object_list.count(), 6)


class FixturesSeasonListViewTest(SimpleDB):
    def setUp(self):
        self.name = "match:fixtures"
        self.url = "/match/fixtures/"

        self.sample_user = User.objects.first()

    def test_view_url_does_not_exist_when_user_is_not_authenticated(self):
        response = self.client.get(self.url)

        self.assertRedirects(response, f"/login/?next={self.url}")

    def test_view_url_exist_at_desired_location_when_user_is_authenticated(
        self,
    ):
        self.client.login(username=self.sample_user.username, password="1_test_TEST_!")

        response = self.client.get(self.url)
        self.assertEquals(response.status_code, HTTPStatus.OK)

    def test_should_return_six_matches(
        self,
    ):
        self.client.login(username=self.sample_user.username, password="1_test_TEST_!")

        response = self.client.get(self.url)
        object_list = response.context["object_list"]
        self.assertEquals(object_list.count(), 6)
