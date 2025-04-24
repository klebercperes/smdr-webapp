from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site

class Command(BaseCommand):
    help = 'Sets up the default site'

    def handle(self, *args, **options):
        site, created = Site.objects.get_or_create(
            id=2,
            defaults={
                'domain': 'peres.au',
                'name': 'peres.au'
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Successfully created site'))
        else:
            self.stdout.write(self.style.SUCCESS('Site already exists')) 