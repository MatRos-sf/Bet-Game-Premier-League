from django.db import models
from django.contrib.auth.models import User
from django.db.models import QuerySet
from django.urls import reverse
from django.db.models import Sum

from PIL import Image


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(
        default="default.jpg", upload_to="profile_pics", verbose_name="profile picture"
    )

    following = models.ManyToManyField(User, related_name="following", blank=True)
    support_team = models.ForeignKey(
        "league.Team",
        on_delete=models.CASCADE,
        related_name="fans",
        blank=True,
        null=True,
    )
    description = models.TextField(max_length=500, blank=True, null=True)

    def __str__(self) -> str:
        return f"{self.user.username}"

    def save(self, *args, **kwargs) -> None:
        super().save(*args, **kwargs)

        img = Image.open(self.image.path)
        if img.height > 300 or img.width > 300:
            max_size = (300, 300)
            img.thumbnail(max_size)
            img.save(self.image.path)

    def get_absolute_url(self) -> str:
        return reverse("profile-detail", args=[str(self.user.username)])

    @property
    def all_points(self) -> int:
        """
        Returns all user points.
        """
        points = self.points.aggregate(total_points=Sum("points"))["total_points"]
        return points if points else 0

    @classmethod
    def followers(cls, user: User) -> QuerySet:
        """
        The method displays a list of all users who are following the specified user.
        """
        return cls.objects.filter(following=user)

    def unfollow(self, username) -> None:
        user = User.objects.get(username=username)
        self.following.remove(user)
        self.save()


class UserScores(models.Model):
    profile = models.ForeignKey(
        Profile, related_name="points", on_delete=models.CASCADE
    )
    points = models.IntegerField(default=0)
    description = models.TextField(max_length=500)
    got = models.DateTimeField(auto_now_add=True)

    @staticmethod
    def render_description(pt, action) -> str:
        """
        This way should be description.
        pt -> points
        action -> for what
        """
        return f"{pt} pt for: {action}."
