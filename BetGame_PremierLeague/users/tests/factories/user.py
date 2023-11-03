import factory

from django.contrib.auth.models import User


class RandomUserFactory(factory.Factory):
    class Meta:
        model = User
