from django.db import models


class Show(models.Model):
    gid = models.IntegerField(null=True)
    id = models.IntegerField(primary_key=True)
    title = models.TextField(null=True, blank=True)
    start_date = models.DateField()
    end_date = models.DateField()

    def __unicode__(self):
        return self.title

    def __str__(self):
        return self.title


class Episode(models.Model):
    id = models.IntegerField(primary_key=True, unique=True)
    show = models.ForeignKey(Show, related_name='episode_show', blank=True, null=True, on_delete=models.CASCADE)
    air_date = models.DateField()
    title = models.TextField()
    slug = models.TextField()

    def __unicode__(self):
        return self.title

    def __str__(self):
        return self.title
