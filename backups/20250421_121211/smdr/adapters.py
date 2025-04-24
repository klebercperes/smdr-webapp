from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.socialaccount.models import SocialApp
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.core.exceptions import ImproperlyConfigured
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
            
    def get_default_redirect_url(self, request, socialaccount=None):
        """
        Return the default redirect URL after successful authentication.
        """
        try:
            # Try to get the URL from settings first
            from django.conf import settings
            if hasattr(settings, 'LOGIN_REDIRECT_URL'):
                try:
                    return reverse(settings.LOGIN_REDIRECT_URL)
                except:
                    logger.warning(f"Could not reverse URL {settings.LOGIN_REDIRECT_URL}, falling back to root URL")
                    return '/'
            
            # Fallback to the namespaced URL
            return reverse('smdr:home')
        except Exception as e:
            logger.error(f"Error getting redirect URL: {str(e)}")
            # Fallback to the root URL if all else fails
            return '/'
            
    def is_auto_signup_allowed(self, request, sociallogin):
        """
        Enable auto signup for social accounts.
        """
        return True
        
    def save_user(self, request, sociallogin, form=None):
        """
        Save the user and ensure email is verified.
        """
        user = super().save_user(request, sociallogin, form)
        if sociallogin.account.provider == 'google':
            # Ensure email is verified for Google accounts
            email_address = sociallogin.email_addresses[0]
            email_address.verified = True
            email_address.primary = True
            email_address.save()
        return user 