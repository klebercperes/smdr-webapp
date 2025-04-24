from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from smdr.models import UserProfile

class Command(BaseCommand):
    help = 'Creates UserProfile for all existing users who don\'t have one'

    def handle(self, *args, **options):
        User = get_user_model()
        users_without_profiles = User.objects.filter(profile__isnull=True)
        
        count = 0
        for user in users_without_profiles:
            UserProfile.objects.create(user=user)
            count += 1
            self.stdout.write(f'Created profile for user: {user.username}')
        
        self.stdout.write(self.style.SUCCESS(f'Successfully created {count} user profiles')) 