import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smdrproject.settings')
django.setup()

from django.contrib.sites.models import Site

# First, get all existing sites
sites = Site.objects.all()
print("Existing sites:")
for site in sites:
    print(f"ID: {site.id}, Domain: {site.domain}, Name: {site.name}")

# Find the site with domain 'peres.au'
try:
    site = Site.objects.get(domain='peres.au')
    print(f"\nFound existing site: ID={site.id}, Domain={site.domain}")
    
    # Update the site to have ID 2
    site.id = 2
    site.save()
    print("Updated site ID to 2")
except Site.DoesNotExist:
    print("\nNo site found with domain 'peres.au'")
    # Create new site
    site = Site.objects.create(
        id=2,
        domain='peres.au',
        name='peres.au'
    )
    print("Created new site with ID 2")

# Verify the final state
print("\nFinal site configuration:")
site = Site.objects.get(id=2)
print(f"ID: {site.id}, Domain: {site.domain}, Name: {site.name}") 