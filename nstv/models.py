from django.db import models
from django.conf import settings

try:
    settings.configure()
except RuntimeError:  # settings already configured
    pass


class Show(models.Model):
    gid = models.IntegerField(null=True)
    title = models.TextField()
    start_date = models.DateField(null=True)
    end_date = models.DateField(null=True)

    def get_absolute_url(self):
        return "/shows/{}".format(str(self.id))

    def __str__(self):
        return self.title

    class Meta:
        db_table = "show"


class Episode(models.Model):
    show = models.ForeignKey(
        Show,
        related_name="episode_show",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )
    air_date = models.DateField(null=True)
    title = models.TextField()
    season_number = models.IntegerField(null=True)
    number = models.IntegerField(null=True)

    def __str__(self):
        return self.title

    class Meta:
        db_table = "episode"