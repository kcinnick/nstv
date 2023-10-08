from django.test import TestCase, Client
from django.urls import reverse

from nstv.models import Movie


class AddMoviePageTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.form_data = {
            "title": "Test Movie",
        }

    def test_uses_add_movie_template(self):
        response = self.client.get('/add_movie')
        self.assertTemplateUsed(response, 'add_movie.html')

    def test_can_save_a_POST_request(self):
        response = self.client.post('/add_movie', data=self.form_data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Movie.objects.count(), 1)
        movie = Movie.objects.first()
        for key, value in self.form_data.items():
            self.assertEqual(getattr(movie, key), value)

    def test_only_saves_items_when_necessary(self):
        self.client.get('/add_movie')
        self.assertEqual(Movie.objects.count(), 0)

    def test_renders_after_POST(self):
        response = self.client.post('/add_movie', data={'title': 'A new movie title'})
        self.assertEqual(response.status_code, 302)

    def test_displays_all_list_items(self):
        Movie.objects.create(title='movie title 1', gid=1)
        Movie.objects.create(title='movie title 2', gid=2)

        response = self.client.get('/movies_index')

        self.assertIn('movie title 1', response.content.decode())
        self.assertIn('movie title 2', response.content.decode())

    def test_can_save_a_POST_request_to_an_existing_list(self):
        Movie.objects.create(title='movie title 1', gid=1)
        Movie.objects.create(title='movie title 2', gid=2)

        self.client.post('/add_movie', data={'title': 'A new movie title'})

        response = self.client.get('/movies_index')
        self.assertIn("A new movie title", response.content.decode())

    def test_redirects_after_POST(self):
        response = self.client.post('/add_movie', data=self.form_data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['location'], '/movies_index')

    def test_redirects_after_duplicate_POST(self):
        Movie.objects.create(title='movie title 1', gid=1)
        Movie.objects.create(title='movie title 2', gid=2)

        response = self.client.post('/add_movie', data={'title': 'movie title 1'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['location'], '/movies_index')
