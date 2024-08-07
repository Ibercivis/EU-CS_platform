from django.core.management.base import BaseCommand
import requests
import time
from projects.models import ProjectCountry

class Command(BaseCommand):
    help = 'Updates country coordinates from Nominatim'

    def handle(self, *args, **options):
        base_url = "https://nominatim.openstreetmap.org/search"
        headers = {'User-Agent': 'eucitizenscience'}

        for country in ProjectCountry.objects.filter(latitude__isnull=True):
            params = {
                'country': country.country.name,
                'format': 'json',
                'limit': 1
            }
            try:
                response = requests.get(base_url, params=params, headers=headers)
                data = response.json()
                if data:
                    country.latitude = float(data[0]['lat'])
                    country.longitude = float(data[0]['lon'])
                    country.save()
                    self.stdout.write(self.style.SUCCESS(f'Successfully updated {country.country.name}'))
                else:
                    self.stdout.write(self.style.WARNING(f'No data found for {country.country.name}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Failed to update {country.country.name}: {str(e)}'))
            
            time.sleep(4)  # Sleep for 4 seconds to respect Nominatim's usage policy
        
        self.stdout.write(self.style.SUCCESS('Finished updating all countries'))