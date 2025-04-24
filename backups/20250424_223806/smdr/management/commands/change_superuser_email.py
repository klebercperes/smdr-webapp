from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = 'Change the email address of the superuser'

    def add_arguments(self, parser):
        parser.add_argument('new_email', type=str, help='New email address for the superuser')

    def handle(self, *args, **options):
        User = get_user_model()
        try:
            superuser = User.objects.filter(is_superuser=True).first()
            if not superuser:
                self.stdout.write(self.style.ERROR('No superuser found'))
                return

            old_email = superuser.email
            new_email = options['new_email']
            
            superuser.email = new_email
            superuser.save()
            
            # Also update the profile email if it exists
            if hasattr(superuser, 'profile'):
                superuser.profile.email = new_email
                superuser.profile.save()

            self.stdout.write(self.style.SUCCESS(f'Successfully changed superuser email from {old_email} to {new_email}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error changing superuser email: {str(e)}')) 