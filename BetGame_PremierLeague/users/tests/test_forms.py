from django.test import TestCase

from users.forms import UserRegisterForm


class UserRegisterFormTest(TestCase):
    def test_form_should_valid_if_all_fields_all_correctly(self):
        payload = {
            "username": "TestUsername",
            "email": "test@email.com",
            "password1": "TESTpassword1",
            "password2": "TESTpassword1",
        }
        form = UserRegisterForm(data=payload)
        self.assertTrue(form.is_valid())

    def test_form_should_invalid_when_passwords_are_different(self):
        payload = {
            "username": "TestUsername",
            "email": "test@email.com",
            "password1": "TESTpassword1",
            "password2": "TESTpassword2",
        }
        form = UserRegisterForm(data=payload)
        self.assertFalse(form.is_valid())

    def test_should_invalid_when_form_doesnt_have_email(self):
        payload = {
            "username": "TestUsername",
            "password1": "TESTpassword1",
            "password2": "TESTpassword1",
        }
        form = UserRegisterForm(data=payload)
        self.assertFalse(form.is_valid())
