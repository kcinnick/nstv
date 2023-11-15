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
    tvdb_id = models.TextField(default=None, null=True)
    cast = models.ManyToManyField('CastMember', related_name='shows')

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
    tvdb_id = models.IntegerField(default=None, null=True)
    cast = models.ManyToManyField('CastMember', related_name='episodes')

    def __str__(self):
        return self.title

    class Meta:
        db_table = "episode"


class Movie(models.Model):
    gid = models.IntegerField(default=None, null=True)
    name = models.TextField()  # title is a reserved word
    release_date = models.DateField(default=None, null=True)
    genre = ArrayField(
        models.CharField(max_length=200, blank=True),
        default=list,
    )
    director = models.TextField()
    on_disk = models.BooleanField(default=False)
    poster_path = models.TextField(default=None, null=True)
    cast = models.ManyToManyField('CastMember', related_name='movies')

    def __str__(self):
        return self.title

    def get_absolute_url(self: 'Movie'):
        return f"/movies/{self.id}"

    class Meta:
        db_table = "movie"


class CastMember(models.Model):
    name = models.TextField()
    role = models.TextField()
    image_url = models.TextField(null=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "cast_member"


class Download(models.Model):
    nzb_id = models.TextField(default=None, null=True)
    site = models.TextField(default=None, null=True)
    title = models.TextField()
    url = models.TextField(default=None, null=True)
    successful = models.BooleanField(default=False)

    def __str__(self):
        return self.title, self.site

    class Meta:
        db_table = "download"
