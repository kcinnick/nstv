from django.db import models
from django.conf import settings

try:
    settings.configure()
except RuntimeError:  # settings already configured
    pass


class Show(models.Model):
    gid = models.IntegerField(default=None)
    title = models.TextField()
    start_date = models.DateField(default=None)
    end_date = models.DateField(default=None)
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
