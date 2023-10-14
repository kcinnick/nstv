from django.db import models
from django.conf import settings
from django.contrib.postgres.fields import ArrayField

try:
    settings.configure()
except RuntimeError:  # settings already configured
    pass


class Show(models.Model):
    gid = models.IntegerField(default=None, null=True)
    title = models.TextField()
    anime = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    class Meta:
        db_table = "show"


class Episode(models.Model):
    show = models.ForeignKey(
        Show,
        related_name="episodes",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )
    air_date = models.DateField(null=True)
    title = models.TextField()
    season_number = models.IntegerField(null=True)
    episode_number = models.IntegerField(null=True)
    on_disk = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    class Meta:
        db_table = "episode"


class Movie(models.Model):
    gid = models.IntegerField(default=None, null=True)
    title = models.TextField()
    release_date = models.DateField(default=None, null=True)
    genre = ArrayField(
        models.CharField(max_length=200, blank=True),
        default=list,
    )
    director = models.TextField()
    on_disk = models.BooleanField(default=False)
    poster_path = models.TextField(default=None, null=True)

    def __str__(self):
        return self.title

    class Meta:
        db_table = "movie"
