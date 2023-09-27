from django.test import TestCase

from nstv.models import Show, Episode


class DeleteTestCase(TestCase):
    def setUp(self):
        self.dummy_show_record = Show.objects.create(title='Dummy show to be deleted.')
        self.dummy_show_episode_record = Episode.objects.create(
            show=self.dummy_show_record,
            air_date='2021-01-01',
            title='Dummy episode to be deleted.',
            season_number=1,
            episode_number=1,
            on_disk=False
        )

    def tearDown(self):
        # Delete the record after each test
        self.dummy_show_record.delete()

    def test_delete_show(self):
        self.client.post('/delete/{}'.format(self.dummy_show_record.id))
        with self.assertRaises(Show.DoesNotExist):
            Show.objects.get(title='Dummy show to be deleted.')

    def test_delete_show_GET_request_fails(self):
        with self.assertRaises(Exception):
            self.client.get('/delete/{}'.format(self.dummy_show_record.id))

    def test_delete_episode_of_show(self):
        self.client.post('/delete/{}/episode/{}'.format(self.dummy_show_record.id, self.dummy_show_record.episodes.first().id))
        with self.assertRaises(Exception):
            Episode.objects.get(title='Dummy episode to be deleted.')

    def test_delete_episode_of_show_GET_request_fails(self):
        with self.assertRaises(Exception):
            self.client.get('/delete/{}/episode/{}'.format(self.dummy_show_record.id, self.dummy_show_record.episodes.first().id))
