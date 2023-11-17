from django.test import TestCase
from nstv.models import Show, Episode


class ShowIndexTest(TestCase):
    def setUp(self):
        self.show = Show.objects.create(title='show title 1', gid=1)

    def test_uses_show_template(self):
        response = self.client.get(f'/shows/{self.show.id}')
        self.assertTemplateUsed(response, 'show.html')

    def test_displays_all_episodes(self):
        Episode.objects.create(show=self.show, title='episode title 1', season_number=1, episode_number=1)
        Episode.objects.create(show=self.show, title='episode title 2', season_number=2, episode_number=2)

        response = self.client.get(f'/shows/{self.show.id}')

        self.assertIn('episode title 1', response.content.decode())
        self.assertIn('episode title 2', response.content.decode())

    def test_show_search(self):
        response = self.client.get('/search/?query=show title 1&shows=on')
        self.assertTemplateUsed(response, 'search.html')
        assert response.status_code == 200
        assert self.show.title in response.content.decode()
