from django.test import TestCase, Client
from django.urls import reverse

from nstv.models import Show, Episode


class AddShowPageTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.form_data = {
            "title": "Test Show",
        }

    def test_uses_add_show_template(self):
        response = self.client.get('/add_show')
        self.assertTemplateUsed(response, 'add_show.html')

    def test_can_save_a_POST_request(self):
        response = self.client.post('/add_show', data=self.form_data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Show.objects.count(), 1)
        show = Show.objects.first()
        for key, value in self.form_data.items():
            self.assertEqual(getattr(show, key), value)

    def test_only_saves_items_when_necessary(self):
        self.client.get('/add_show')
        self.assertEqual(Show.objects.count(), 0)

    def test_renders_after_POST(self):
        response = self.client.post('/add_show', data={'title': 'A new show title'})
        self.assertEqual(response.status_code, 302)

    def test_displays_all_list_items(self):
        Show.objects.create(title='show title 1', gid=1)
        Show.objects.create(title='show title 2', gid=2)

        response = self.client.get('/shows_index')

        self.assertIn('show title 1', response.content.decode())
        self.assertIn('show title 2', response.content.decode())

    def test_can_save_a_POST_request_to_an_existing_list(self):
        Show.objects.create(title='show title 1', gid=1)
        Show.objects.create(title='show title 2', gid=2)

        self.client.post('/add_show', data={'title': 'A new show title'})

        response = self.client.get('/shows_index')
        self.assertIn("A new show title", response.content.decode())

    def test_redirects_after_POST(self):
        response = self.client.post('/add_show', data=self.form_data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['location'], '/shows_index')

    def test_redirects_after_duplicate_POST(self):
        Show.objects.create(title='show title 1', gid=1)
        Show.objects.create(title='show title 2', gid=2)

        response = self.client.post('/add_show', data={'title': 'show title 1'})

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['location'], '/shows_index')
