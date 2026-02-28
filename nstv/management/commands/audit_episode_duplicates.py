from django.core.management.base import BaseCommand
from django.db.models import Count

from nstv.models import Episode, Show


class Command(BaseCommand):
    help = "Audit duplicate episodes by (show, season_number, episode_number), with optional auto-fix."

    def add_arguments(self, parser):
        parser.add_argument('--fix', action='store_true', help='Merge duplicate groups and delete extras.')
        parser.add_argument('--show-id', type=int, help='Restrict audit to a single show id.')

    @staticmethod
    def _merge_episode_group(episodes):
        primary_episode = episodes[0]
        duplicates = episodes[1:]

        for duplicate in duplicates:
            if not primary_episode.on_disk and duplicate.on_disk:
                primary_episode.on_disk = True
            if not primary_episode.tvdb_id and duplicate.tvdb_id:
                primary_episode.tvdb_id = duplicate.tvdb_id
            if not primary_episode.air_date and duplicate.air_date:
                primary_episode.air_date = duplicate.air_date
            if (
                duplicate.title
                and (not primary_episode.title or primary_episode.title.lower().startswith('episode '))
                and not duplicate.title.lower().startswith('episode ')
            ):
                primary_episode.title = duplicate.title

            duplicate.delete()

        primary_episode.save()
        return len(duplicates)

    def handle(self, *args, **options):
        should_fix = options['fix']
        show_id = options.get('show_id')

        episodes = Episode.objects.exclude(season_number__isnull=True).exclude(episode_number__isnull=True)
        if show_id:
            episodes = episodes.filter(show_id=show_id)

        duplicate_groups = (
            episodes
            .values('show_id', 'season_number', 'episode_number')
            .annotate(total=Count('id'))
            .filter(total__gt=1)
            .order_by('-total', 'show_id', 'season_number', 'episode_number')
        )

        if not duplicate_groups.exists():
            self.stdout.write(self.style.SUCCESS('No duplicate episode groups found.'))
            return

        self.stdout.write(self.style.WARNING(f'Found {duplicate_groups.count()} duplicate group(s).'))

        deleted_count = 0

        for group in duplicate_groups:
            show = Show.objects.filter(id=group['show_id']).first()
            show_title = show.title if show else f"Show {group['show_id']}"
            self.stdout.write(
                f"- {show_title} S{group['season_number']}E{group['episode_number']} has {group['total']} rows"
            )

            if should_fix:
                group_episodes = list(
                    Episode.objects.filter(
                        show_id=group['show_id'],
                        season_number=group['season_number'],
                        episode_number=group['episode_number'],
                    ).order_by('-on_disk', '-tvdb_id', 'id')
                )
                deleted_count += self._merge_episode_group(group_episodes)

        if should_fix:
            self.stdout.write(self.style.SUCCESS(f'Fixed duplicate groups. Deleted {deleted_count} extra row(s).'))
        else:
            self.stdout.write(self.style.WARNING('Dry run only. Re-run with --fix to merge duplicates.'))
