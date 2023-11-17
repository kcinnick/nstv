from django.test import TestCase, Client
from django.urls import reverse

from nstv.models import CastMember, Show, Movie


class CastMemberTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.test_cast_member = CastMember.objects.create(name='Test Cast Member')

        self.test_show = Show.objects.create(title='Test Show', gid=1)
        self.test_movie = Movie.objects.create(name='Test Movie', gid=2)

        self.test_cast_member.shows.add(self.test_show)
        self.test_cast_member.movies.add(self.test_movie)

    def test_cast_member_page(self):
        response = self.client.get(f'/cast/{self.test_cast_member.id}')
        self.assertTemplateUsed(response, 'cast_member.html')
        self.assertIn('Test Cast Member', response.content.decode())
        self.assertIn('Test Show', response.content.decode())
        self.assertIn('Test Movie', response.content.decode())

    def test_cast_member_search(self):
        response = self.client.get('/search/?query=Test Cast Member&cast_members=on')
        print(response.content)
        self.assertTemplateUsed(response, 'search.html')
        assert response.status_code == 200
        assert 'Test Cast Member' in response.content.decode()