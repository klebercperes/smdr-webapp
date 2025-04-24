import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smdrproject.settings')
os.environ['DJANGO_SETTINGS_MODULE'] = 'smdrproject.settings'
os.environ['PYTHONPATH'] = '/home/kleber/smdr'

# Disable logging
import logging
logging.disable(logging.CRITICAL)

django.setup()

from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp

def check_and_configure_social_app():
    # Check if site exists by domain
    try:
        site = Site.objects.get(domain='peres.au')
        print(f"Site found with domain 'peres.au' and id={site.id}")
        
        # Update site ID if needed
        if site.id != 2:
            print(f"Updating site ID from {site.id} to 2...")
            old_id = site.id
            site.id = 2
            site.save()
            # Delete the old site to avoid conflicts
            Site.objects.filter(id=old_id).delete()
            print("Site ID updated successfully")
    except Site.DoesNotExist:
        print("Site with domain 'peres.au' does not exist. Creating...")
        site = Site.objects.create(id=2, domain='peres.au', name='peres.au')
        print(f"Created site with id={site.id}")

    # Check if social app exists
    try:
        social_app = SocialApp.objects.get(provider='google')
        print(f"Google social app found with client_id: {social_app.client_id}")
        
        # Update the client ID and secret if they don't match
        if social_app.client_id != os.getenv('GOOGLE_CLIENT_ID') or social_app.secret != os.getenv('GOOGLE_CLIENT_SECRET'):
            print("Updating Google social app credentials...")
            social_app.client_id = os.getenv('GOOGLE_CLIENT_ID')
            social_app.secret = os.getenv('GOOGLE_CLIENT_SECRET')
            social_app.save()
            print("Google social app credentials updated")
            
        # Ensure the site is associated
        if site not in social_app.sites.all():
            social_app.sites.add(site)
            print("Added site to Google social app")
            
    except SocialApp.DoesNotExist:
        print("Google social app does not exist. Creating...")
        social_app = SocialApp.objects.create(
            provider='google',
            name='Google',
            client_id=os.getenv('GOOGLE_CLIENT_ID'),
            secret=os.getenv('GOOGLE_CLIENT_SECRET')
        )
        social_app.sites.add(site)
        print("Created Google social app")

if __name__ == '__main__':
    check_and_configure_social_app() 