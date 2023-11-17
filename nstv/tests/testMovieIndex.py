from django.test import TestCase
from nstv.models import Movie


class MovieIndexTest(TestCase):
    def setUp(self):
        # Create a record before each test
        self.movie_object = Movie(
            name='Goldfinger', gid=1
        )
        self.movie_object.save()

    def test_uses_movie_template(self):
        response = self.client.get(f'/movies/{self.movie_object.id}')
        self.assertTemplateUsed(response, 'movie.html')

    def test_movie_search(self):
        response = self.client.get('/search/?query=Goldfinger&movies=on')
        self.assertTemplateUsed(response, 'search.html')
        assert response.status_code == 200
        assert 'Goldfinger' in response.content.decode()

    def test_movie_not_in_db_search(self):
        self.movie_object.delete()
        response = self.client.get('/search/?query=Goldfinger&movies=on')
        self.assertTemplateUsed(response, 'search.html')
        assert response.status_code == 200
        assert 'Goldfinger' not in response.content.decode()
