from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User


from users.forms import UserRegisterForm
from users.models import Profile


class RegisterTest(TestCase):

    def test_view_url_exist_at_desired_location(self):
        response = self.client.get('/register/')
        self.assertEquals(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('register'))
        self.assertEquals(response.status_code, 200)

    def test_view_uses_correctly_templates(self):
        response = self.client.get(reverse('register'))

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/register.html')

    def test_post_should_redirect_when_form_is_valid(self):
        payload = {
            'username': 'test',
            'email': 'test@test.pl',
            'password1': '{5:vhM9Ed[M/VmL',
            'password2': '{5:vhM9Ed[M/VmL'
        }
        response = self.client.post(reverse('register'), data=payload)

        self.assertRedirects(response, reverse('login'))

    def test_post_should_show_messages_when_form_is_valid(self):
        payload = {
            'username': 'test',
            'email': 'test@test.pl',
            'password1': '{5:vhM9Ed[M/VmL',
            'password2': '{5:vhM9Ed[M/VmL'
        }

        response = self.client.post(reverse('register'), data=payload, follow=True)
        expected_message = f"Dear {payload['username']}, you have been successfully signed up!"

        message = list(response.context.get('messages'))[0]
        self.assertEquals(message.tags, "success")
        self.assertEquals(expected_message, message.message)

    def test_post_should_create_user_and_profile_when_form_is_valid(self):
        payload = {
            'username': 'test',
            'email': 'test@test.pl',
            'password1': '{5:vhM9Ed[M/VmL',
            'password2': '{5:vhM9Ed[M/VmL'
        }

        self.client.post(reverse('register'), data=payload, follow=True)

        self.assertTrue(User.objects.get(username=payload['username']))
        self.assertTrue(Profile.objects.get(user__username=payload['username']))

    def test_post_should_not_create_user_and_profile_when_form_is_invalid(self):
        payload = {
            'username': 'test',
            'password1': '{5:vhM9Ed[M/VmL',
            'password2': '{5:vhM9Ed[M/VmL'
        }

        self.client.post(reverse('register'), data=payload, follow=True)

        self.assertFalse(User.objects.filter(username=payload['username']).exists())
        self.assertFalse(Profile.objects.filter(user__username=payload['username']).exists())