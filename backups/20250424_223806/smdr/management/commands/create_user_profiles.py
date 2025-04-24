from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from smdr.models import UserProfile

class Command(BaseCommand):
    help = 'Ensures all users have associated profiles'

    def handle(self, *args, **kwargs):
        users = User.objects.all()
        created = 0
        existing = 0

        for user in users:
            try:
                profile = user.profile
                existing += 1
            except UserProfile.DoesNotExist:
                UserProfile.objects.create(user=user)
                created += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully processed all users. '
                f'Created {created} new profiles, '
                f'{existing} profiles already existed.'
            )
        ) 