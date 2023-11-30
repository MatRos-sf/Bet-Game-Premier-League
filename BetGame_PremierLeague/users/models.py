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

    @classmethod
    def position(cls, profile: str):
        p = (
            cls.objects.annotate(total_points=Sum("points__points"))
            .order_by("-total_points")
            .values_list("user__username", flat=True)
        )
        p = list(p).index(profile)

        return p + 1

    @classmethod
    def top_players(cls, end: int) -> QuerySet:
        if end < 1:
            raise ValueError("End cannot be lower than 1.")

        return (
            cls.objects.annotate(sum_points=Sum("points__points", default=0))
            .select_related("user")
            .order_by("-sum_points")[:end]
        )

    def unfollow(self, pk: int) -> None:
        self.following.remove(pk)
        self.save()

    def follow(self, user_id: int):
        self.following.add(user_id)
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
