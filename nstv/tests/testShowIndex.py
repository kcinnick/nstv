from django.test import TestCase
from nstv.models import Show, Episode


class ShowIndexTest(TestCase):
    def test_uses_show_template(self):
        show = Show.objects.create(title='show title 1', gid=1)
        response = self.client.get(f'/shows/{show.id}')
        self.assertTemplateUsed(response, 'show.html')

    def test_displays_all_episodes(self):
        show = Show.objects.create(title='show title 1', gid=1)
        Episode.objects.create(show=show, title='episode title 1', season_number=1, number=1)
        Episode.objects.create(show=show, title='episode title 2', season_number=2, number=2)

        response = self.client.get(f'/shows/{show.id}')

        self.assertIn('episode title 1', response.content.decode())
        self.assertIn('episode title 2', response.content.decode())
