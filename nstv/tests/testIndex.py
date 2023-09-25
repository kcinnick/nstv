from django.test import TestCase

from nstv.models import Show, Episode


class IndexTest(TestCase):
    def setUp(self):
        # Create a record before each test
        self.show_object = Show(
            title='Seinfeld', anime=False, gid='79169'
        )
        self.show_object.save()

    def tearDown(self):
        # Delete the record after each test
        self.show_object.delete()

    def test_uses_index_template(self):
        response = self.client.get('/')
        self.assertTemplateUsed(response, 'index.html')

    def test_displays_all_shows(self):
        response = self.client.get('/')
        self.assertIn(self.show_object.title, response.content.decode())

    def test_can_process_a_POST_request_for_show_that_exists(self):
        response = self.client.post('/', data={
            'show_title': 1,
            'season_number': '1',
            'episode_number': '1',
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Show.objects.count(), 1)
        self.assertTemplateUsed(response, 'index.html')

    def test_cannot_process_a_POST_request_for_show_that_does_not_exist(self):
        response = self.client.post('/', data={
            'show_title': 'show title 2',
            'season_number': '1',
            'episode_number': '1',
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Show.objects.count(), 1)
        self.assertContains(response, 'Select a valid choice. show title 2 is not one of the available choices')

