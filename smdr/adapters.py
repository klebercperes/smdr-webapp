from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.socialaccount.models import SocialApp
from django.contrib.sites.shortcuts import get_current_site
import logging

logger = logging.getLogger(__name__)

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    """
    Custom adapter for social account authentication.
    Handles the retrieval of social apps with improved error handling.
    """
    
    def get_app(self, request, provider, client_id=None):
        """
        Get the social app for the given provider.
        
        Args:
            request: The current request object
            provider: The social provider (e.g., 'google')
            client_id: Optional client ID for the provider
            
        Returns:
            SocialApp: The first matching social app
            
        Raises:
            SocialApp.DoesNotExist: If no app is configured for the site
        """
        try:
            # Get the current site
            site = get_current_site(request)
            logger.debug(f"Getting social app for provider {provider} on site {site.domain}")
            
            # Get all apps for this provider
            apps = SocialApp.objects.filter(
                sites__id=site.id,
                provider=provider
            )
            
            if not apps:
                logger.warning(f"No social app configured for provider {provider} on site {site.domain}")
                raise SocialApp.DoesNotExist(f'No social app configured for provider {provider} on site {site.domain}')
            
            # If multiple apps exist, use the first one
            app = apps.first()
            logger.debug(f"Found social app: {app.name} (ID: {app.id})")
            return app
            
        except Exception as e:
            logger.error(f"Error getting social app: {str(e)}")
            raise 