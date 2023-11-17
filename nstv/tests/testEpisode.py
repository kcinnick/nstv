from django.test import TestCase
from nstv.models import Show, Episode


class EpisodeTestCase(TestCase):
    def setUp(self):
        self.show = Show.objects.create(title='show title 1', gid=1)
        self.episode = Episode.objects.create(show=self.show, title='episode title 1', season_number=1,
                                              episode_number=1)
