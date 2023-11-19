from django.test import tag
from django.contrib.auth.models import User
from http import HTTPStatus
from parameterized import parameterized

from .test_models import SimpleDB


@tag("team_detal_view")
class TeamDetailViewTest(SimpleDB):
    def setUp(self):
        self.url = lambda x: f"/league/team/{x}/"
        self.name = "team-detail"

        self.sample_user = User.objects.first()

    @parameterized.expand([1, 2, 3, 4])
    def test_view_url_does_not_exist_when_user_is_not_authenticated(self, pk):
        response = self.client.get(self.url(pk))

        self.assertRedirects(response, f"/login/?next={self.url(pk)}")

    @parameterized.expand([1, 2, 3, 4])
    def test_view_url_exist_at_desired_location_when_user_is_authenticated(self, pk):
        self.client.login(username=self.sample_user.username, password="1_test_TEST_!")
        response = self.client.get(self.url(pk))
        self.assertEquals(response.status_code, HTTPStatus.OK)
