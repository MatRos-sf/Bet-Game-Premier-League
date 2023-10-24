from django.db import models
from django.contrib.auth.models import User
from PIL import Image
from django.urls import reverse


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(default='default.jpg', upload_to='profile_pics', verbose_name='profile picture')

    friends = models.ManyToManyField(User, related_name='friends')
    support_team = models.ForeignKey('league.Team', on_delete=models.CASCADE, related_name="fans",
                                     blank=True, null=True)
    def get_absolute_url(self):
        return reverse('user-profile-detail', args=[str(self.user.username)])

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        img = Image.open(self.image.path)
        if img.height > 300 or img.width > 300:
            max_size = (300, 300)
            img.thumbnail(max_size)
            #img = img.resize(max_size, Image.BOX)
            img.save(self.image.path)

    def __str__(self):
        return f"{self.user.username}"


class SeasonPoints(models.Model):

    profile = models.ForeignKey(Profile, related_name='points', on_delete=models.CASCADE)
    points = models.IntegerField(default=0)
    season = models.ForeignKey('league.Season', on_delete=models.CASCADE)
    current = models.BooleanField(default=True)


