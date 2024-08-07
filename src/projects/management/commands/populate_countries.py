from django.core.management.base import BaseCommand
from django_countries import countries
from projects.models import ProjectCountry

class Command(BaseCommand):
    help = 'Populates the database with countries from django-countries'

    def handle(self, *args, **options):
        # First, clear existing data to prevent duplicates
        ProjectCountry.objects.all().delete()

        # Now, populate the database
        for code, name in countries:
            ProjectCountry.objects.create(country=code)

        self.stdout.write(self.style.SUCCESS('Successfully populated countries'))
