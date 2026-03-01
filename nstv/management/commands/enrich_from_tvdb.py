"""
Django management command to enrich shows with metadata from TVDB.
Fetches overview, first_aired, status, network, genres, poster_url, and rating
for shows that have a tvdb_id but are missing metadata fields.
"""
import os
from datetime import datetime
from django.core.management.base import BaseCommand
from nstv.models import Show
import tvdb_v4_official


class Command(BaseCommand):
    help = 'Enrich shows with metadata from TVDB API'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be changed without making changes',
        )
        parser.add_argument(
            '--show-id',
            type=int,
            help='Process only a specific show by ID',
        )

    def _fetch_and_update_metadata(self, tvdb, show, dry_run=False):
        """
        Fetch metadata from TVDB and update the show model.
        """
        if not show.tvdb_id:
            self.stdout.write(
                self.style.WARNING(f'  ⚠ {show.title}: No TVDB ID, skipping')
            )
            return False

        try:
            tvdb_series = tvdb.get_series(show.tvdb_id)
            updates = []
            has_updates = False

            # Check and update each field
            if tvdb_series.get('overview') and not show.overview:
                has_updates = True
                if dry_run:
                    updates.append(f'overview: "{tvdb_series["overview"][:50]}..."')
                else:
                    show.overview = tvdb_series['overview']

            if tvdb_series.get('firstAired') and not show.first_aired:
                try:
                    first_aired = datetime.strptime(tvdb_series['firstAired'], '%Y-%m-%d').date()
                    has_updates = True
                    if dry_run:
                        updates.append(f'first_aired: {first_aired}')
                    else:
                        show.first_aired = first_aired
                except ValueError:
                    pass

            if tvdb_series.get('status') and not show.status:
                status = tvdb_series['status'].get('name') if isinstance(tvdb_series['status'], dict) else tvdb_series['status']
                has_updates = True
                if dry_run:
                    updates.append(f'status: {status}')
                else:
                    show.status = status

            if tvdb_series.get('originalNetwork') and not show.network:
                has_updates = True
                if dry_run:
                    updates.append(f'network: {tvdb_series["originalNetwork"]}')
                else:
                    show.network = tvdb_series['originalNetwork']

            if tvdb_series.get('genres') and not show.genre:
                genres = []
                for genre in tvdb_series['genres']:
                    if isinstance(genre, dict):
                        genres.append(genre.get('name', ''))
                    else:
                        genres.append(str(genre))
                genres = [g for g in genres if g]
                if genres:
                    has_updates = True
                    if dry_run:
                        updates.append(f'genres: {", ".join(genres)}')
                    else:
                        show.genre = genres

            if tvdb_series.get('image') and not show.poster_url:
                has_updates = True
                if dry_run:
                    updates.append(f'poster_url: {tvdb_series["image"]}')
                else:
                    show.poster_url = tvdb_series['image']

            # Note: Skipping score/rating for now as TVDB's score is not a 0-10 rating
            # but rather a popularity score that can be very large (thousands)
            # if tvdb_series.get('score') and not show.rating:
            #     try:
            #         rating = round(float(tvdb_series['score']), 1)
            #         has_updates = True
            #         if dry_run:
            #             updates.append(f'rating: {rating}')
            #         else:
            #             show.rating = rating
            #     except (ValueError, TypeError):
            #         pass

            if has_updates:
                if dry_run:
                    self.stdout.write(f'  Would update {show.title}:')
                    for update in updates:
                        self.stdout.write(f'    - {update}')
                else:
                    show.save()
                    self.stdout.write(
                        self.style.SUCCESS(f'  ✓ Updated {show.title}')
                    )
                return True
            else:
                self.stdout.write(f'  → {show.title}: Already has all metadata')
                return False

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'  ✗ {show.title}: Error fetching metadata - {str(e)}')
            )
            return False

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        show_id = options.get('show_id')

        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be made\n'))

        # Initialize TVDB API
        api_key = os.getenv('TVDB_API_KEY')
        if not api_key:
            self.stdout.write(
                self.style.ERROR('TVDB_API_KEY environment variable not set')
            )
            return

        try:
            tvdb = tvdb_v4_official.TVDB(api_key)
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Failed to initialize TVDB API: {str(e)}')
            )
            return

        # Get shows to process
        if show_id:
            try:
                shows = [Show.objects.get(id=show_id)]
            except Show.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'Show with ID {show_id} not found')
                )
                return
        else:
            shows = Show.objects.filter(tvdb_id__isnull=False)

        self.stdout.write(f'Processing {len(shows)} show(s)...\n')

        updated_count = 0
        for show in shows:
            if self._fetch_and_update_metadata(tvdb, show, dry_run):
                updated_count += 1

        self.stdout.write('')
        if updated_count == 0:
            self.stdout.write(self.style.SUCCESS('No shows needed enrichment'))
        else:
            action = 'Would enrich' if dry_run else 'Enriched'
            self.stdout.write(
                self.style.SUCCESS(f'{action} {updated_count} show(s)')
            )
