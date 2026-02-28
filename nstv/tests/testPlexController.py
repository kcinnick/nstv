from datetime import date
from types import SimpleNamespace

from django.test import TestCase

from nstv.models import Episode, Movie, Show
from nstv.plexController.add_episodes_to_show import add_existing_episodes_for_plex_show
from nstv.plexController.add_movies_to_nstv import upsert_movie_from_plex_movie
from nstv.plexController.add_shows_to_nstv import _is_anime_by_genres, upsert_show_from_plex_show


class PlexControllerTest(TestCase):
    def test_is_anime_by_genres_detects_anime(self):
        self.assertTrue(_is_anime_by_genres(['Drama', 'Anime']))
        self.assertTrue(_is_anime_by_genres(['Animation']))
        self.assertFalse(_is_anime_by_genres(['Drama']))

    def test_upsert_show_creates_new_show(self):
        plex_show = SimpleNamespace(title='Solo Leveling', genres=['Anime'])

        show, created = upsert_show_from_plex_show(plex_show)

        self.assertTrue(created)
        self.assertEqual(show.title, 'Solo Leveling')
        self.assertTrue(show.anime)

    def test_upsert_show_updates_existing_show_anime_flag(self):
        Show.objects.create(title='Arcane', anime=False)
        plex_show = SimpleNamespace(title='Arcane', genres=['Animation'])

        show, created = upsert_show_from_plex_show(plex_show)

        self.assertFalse(created)
        self.assertTrue(show.anime)

    def test_upsert_movie_creates_movie(self):
        plex_movie = SimpleNamespace(
            title='Interstellar',
            originallyAvailableAt=date(2014, 11, 7),
            genres=[SimpleNamespace(tag='Sci-Fi')],
            directors=[SimpleNamespace(tag='Christopher Nolan')],
            posterUrl=None,
        )

        movie, created = upsert_movie_from_plex_movie(plex_movie)

        self.assertTrue(created)
        self.assertEqual(movie.name, 'Interstellar')
        self.assertEqual(movie.genre, ['Sci-Fi'])
        self.assertEqual(movie.director, 'Christopher Nolan')
        self.assertTrue(movie.on_disk)

    def test_upsert_movie_updates_existing_on_disk(self):
        Movie.objects.create(name='Inception', director='Christopher Nolan', on_disk=False)
        plex_movie = SimpleNamespace(
            title='Inception',
            originallyAvailableAt=date(2010, 7, 16),
            genres=[SimpleNamespace(tag='Sci-Fi')],
            directors=[SimpleNamespace(tag='Christopher Nolan')],
            posterUrl=None,
        )

        movie, created = upsert_movie_from_plex_movie(plex_movie)

        self.assertFalse(created)
        self.assertTrue(movie.on_disk)

    def test_add_existing_episodes_creates_new_episode(self):
        show = Show.objects.create(title='Some Show')
        plex_episode = SimpleNamespace(
            title='Pilot',
            seasonNumber=1,
            seasonName='Season 1',
            originallyAvailableAt=date(2024, 1, 1),
            index=1,
        )
        plex_show = SimpleNamespace(title='Some Show', episodes=lambda: [plex_episode])

        created_count, updated_count = add_existing_episodes_for_plex_show(plex_show)

        self.assertEqual(created_count, 1)
        self.assertEqual(updated_count, 0)
        self.assertEqual(Episode.objects.filter(show=show, title='Pilot').count(), 1)

    def test_add_existing_episodes_marks_existing_episode_on_disk(self):
        show = Show.objects.create(title='Another Show')
        Episode.objects.create(
            show=show,
            title='Episode 2',
            season_number=1,
            episode_number=2,
            on_disk=False,
        )
        plex_episode = SimpleNamespace(
            title='Episode 2',
            seasonNumber=1,
            seasonName='Season 1',
            originallyAvailableAt=date(2024, 1, 2),
            index=2,
        )
        plex_show = SimpleNamespace(title='Another Show', episodes=lambda: [plex_episode])

        created_count, updated_count = add_existing_episodes_for_plex_show(plex_show)

        self.assertEqual(created_count, 0)
        self.assertEqual(updated_count, 1)
        self.assertTrue(Episode.objects.get(show=show, title='Episode 2').on_disk)
