from datetime import date
from io import StringIO

from django.core.management import call_command
from django.test import TestCase

from nstv.models import Episode, Show


class AuditEpisodeDuplicatesCommandTest(TestCase):
    def test_dry_run_reports_duplicate_groups(self):
        show = Show.objects.create(title='Analog Squad')
        Episode.objects.create(show=show, title='Episode 1', season_number=1, episode_number=1, on_disk=True)
        Episode.objects.create(show=show, title="There's no turning back", season_number=1, episode_number=1, on_disk=False)

        output = StringIO()
        call_command('audit_episode_duplicates', stdout=output)

        text = output.getvalue()
        self.assertIn('Found 1 duplicate group(s).', text)
        self.assertIn('Dry run only. Re-run with --fix to merge duplicates.', text)

    def test_fix_merges_duplicates_and_preserves_best_fields(self):
        show = Show.objects.create(title='Analog Squad')
        Episode.objects.create(
            show=show,
            title='Episode 1',
            season_number=1,
            episode_number=1,
            on_disk=False,
            tvdb_id=None,
            air_date=None,
        )
        Episode.objects.create(
            show=show,
            title="There's no turning back",
            season_number=1,
            episode_number=1,
            on_disk=True,
            tvdb_id=12345,
            air_date=date(2023, 12, 7),
        )

        call_command('audit_episode_duplicates', '--fix')

        episodes = Episode.objects.filter(show=show, season_number=1, episode_number=1)
        self.assertEqual(episodes.count(), 1)
        episode = episodes.first()
        self.assertTrue(episode.on_disk)
        self.assertEqual(episode.tvdb_id, 12345)
        self.assertEqual(episode.air_date, date(2023, 12, 7))
        self.assertEqual(episode.title, "There's no turning back")
