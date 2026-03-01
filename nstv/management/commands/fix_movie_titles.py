"""
Django management command to fix movie titles that contain years.
Extracts year from title and populates release_date if empty.
"""
import re
from datetime import date
from django.core.management.base import BaseCommand
from nstv.models import Movie


class Command(BaseCommand):
    help = 'Fix movie titles that contain years by extracting year to release_date field'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be changed without making changes',
        )

    def _extract_year_from_title(self, title):
        """
        Extract year from movie title if present.
        Returns (cleaned_title, year_as_date)
        """
        year_pattern = r'\s*[\(]?(\d{4})[\)]?\s*$'
        match = re.search(year_pattern, title)
        
        if match:
            year = int(match.group(1))
            current_year = date.today().year
            if 1900 <= year <= current_year + 5:
                cleaned_title = re.sub(year_pattern, '', title).strip()
                release_date = date(year, 1, 1)
                return cleaned_title, release_date
        
        return title, None

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be made'))
        
        movies = Movie.objects.all()
        fixed_count = 0
        
        for movie in movies:
            cleaned_name, extracted_date = self._extract_year_from_title(movie.name)
            
            # Check if title has a year that should be extracted
            if cleaned_name != movie.name:
                if dry_run:
                    self.stdout.write(
                        f'Would update: "{movie.name}" -> "{cleaned_name}"'
                    )
                    if extracted_date and not movie.release_date:
                        self.stdout.write(f'  Set release_date: {extracted_date}')
                else:
                    old_name = movie.name
                    movie.name = cleaned_name
                    if extracted_date and not movie.release_date:
                        movie.release_date = extracted_date
                    movie.save()
                    self.stdout.write(
                        self.style.SUCCESS(f'✓ Updated: "{old_name}" -> "{cleaned_name}"')
                    )
                    if extracted_date:
                        self.stdout.write(f'  Set release_date: {extracted_date}')
                
                fixed_count += 1
        
        if fixed_count == 0:
            self.stdout.write(self.style.SUCCESS('No movies needed fixing'))
        else:
            action = 'Would fix' if dry_run else 'Fixed'
            self.stdout.write(
                self.style.SUCCESS(f'\n{action} {fixed_count} movie(s)')
            )
