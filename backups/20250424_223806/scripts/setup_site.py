import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smdrproject.settings')
django.setup()

from django.contrib.sites.models import Site

# Create or update the site
site, created = Site.objects.get_or_create(
    id=2,
    defaults={
        'domain': 'peres.au',
        'name': 'peres.au'
    }
)

if created:
    print(f"Successfully created site: {site.domain}")
else:
    print(f"Site already exists: {site.domain}") 