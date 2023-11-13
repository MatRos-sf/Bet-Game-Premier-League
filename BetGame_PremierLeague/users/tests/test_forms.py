from django.test import TestCase
from faker import Faker
from django.test import tag
from django.contrib.auth.models import User

from users.forms import UserRegisterForm
from .factories.user import UserFactory
from users.models import Profile
from .factories.profile import ProfileFactory, ExtendProfileFactory


@tag("form_registration")
class UserRegisterFormTest(TestCase):
    def setUp(self):
        self.fake = Faker()

    def test_form_should_valid_if_all_fields_all_correctly(self):
        fake_password = self.fake.password()
        payload = {
            "username": "username_test",
            "email": self.fake.email(),
            "password1": fake_password,
            "password2": fake_password,
        }
        form = UserRegisterForm(data=payload)
        self.assertTrue(form.is_valid())

    def test_form_should_invalid_when_passwords_are_different(self):
        payload = {
            "username": "TestUsername",
            "email": self.fake.email(),
            "password1": self.fake.password(),
            "password2": self.fake.password() + "2",
        }
        form = UserRegisterForm(data=payload)
        self.assertFalse(form.is_valid())

    def test_should_invalid_when_form_doesnt_have_email(self):
        fake_password = self.fake.password()
        payload = {
            "username": "TestUsername",
            "password1": fake_password,
            "password2": fake_password,
        }

        form = UserRegisterForm(data=payload)
        self.assertFalse(form.is_valid())

    def test_should_invalid_when_user_exists(self):
        UserFactory(username="user_test")
        fake_password = self.fake.password()

        payload = {
            "username": "user_test",
            "password1": fake_password,
            "password2": fake_password,
        }

        form = UserRegisterForm(data=payload)

        self.assertFalse(form.is_valid())

    def test_should_create_new_user_when_form_is_valid(self):
        fake_password = self.fake.password()
        payload = {
            "username": "username_test",
            "email": self.fake.email(),
            "password1": fake_password,
            "password2": fake_password,
        }
        form = UserRegisterForm(data=payload)
        self.assertTrue(form.is_valid())
        form.save()
        self.assertEquals(User.objects.count(), 1)


# class ProfileUpdateTest(TestCase):
