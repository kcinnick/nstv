from django.test import TestCase

from nstv.get_info_from_tvdb.main import merge_duplicate_episodes_for_show, upsert_episode_from_tvdb_listing
from nstv.models import Episode, Show


class TvdbImportDedupTest(TestCase):
    def test_upsert_matches_existing_by_season_episode_and_preserves_on_disk(self):
        show = Show.objects.create(title='Analog Squad')
        episode = Episode.objects.create(
            show=show,
            title='Episode 1',
            season_number=1,
            episode_number=1,
            on_disk=True,
        )

        listing = {
            'id': 12345,
            'name': "There's no turning back",
            'seasonNumber': 1,
            'number': 1,
            'aired': '2023-12-07',
        }

        updated_episode, created = upsert_episode_from_tvdb_listing(show, listing, show.title)

        self.assertFalse(created)
        self.assertEqual(updated_episode.id, episode.id)
        self.assertEqual(updated_episode.title, "There's no turning back")
        self.assertEqual(updated_episode.season_number, 1)
        self.assertEqual(updated_episode.episode_number, 1)
        self.assertTrue(updated_episode.on_disk)
        self.assertEqual(Episode.objects.filter(show=show, season_number=1, episode_number=1).count(), 1)

    def test_merge_duplicate_episodes_keeps_single_on_disk_record(self):
        show = Show.objects.create(title='Analog Squad')
        Episode.objects.create(
            show=show,
            title='Episode 1',
            season_number=1,
            episode_number=1,
            on_disk=True,
            tvdb_id=None,
        )
        Episode.objects.create(
            show=show,
            title="There's no turning back",
            season_number=1,
            episode_number=1,
            on_disk=False,
            tvdb_id=12345,
        )

        merge_duplicate_episodes_for_show(show)

        episodes = Episode.objects.filter(show=show, season_number=1, episode_number=1)
        self.assertEqual(episodes.count(), 1)
        surviving = episodes.first()
        self.assertTrue(surviving.on_disk)
        self.assertEqual(surviving.tvdb_id, 12345)
        self.assertIn(surviving.title, ["There's no turning back", 'Episode 1'])
