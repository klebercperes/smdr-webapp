#!/bin/bash

# Script to manage users and profiles
# Usage: ./manage_users.sh [create_profiles|list_users|create_superuser|change_superuser_email|update_superuser_password]

VENV_PATH="/home/kleber/smdr/venv"
PROJECT_PATH="/home/kleber/smdr"
MANAGE_CMD="$VENV_PATH/bin/python $PROJECT_PATH/manage.py"

# Activate virtual environment
source $VENV_PATH/bin/activate

case "$1" in
    create_profiles)
        echo "Creating profiles for existing users..."
        $MANAGE_CMD create_user_profiles
        ;;
    list_users)
        echo "Listing all users and their profile status..."
        $MANAGE_CMD shell -c "
from django.contrib.auth import get_user_model
from smdr.models import UserProfile
User = get_user_model()
for user in User.objects.all():
    has_profile = UserProfile.objects.filter(user=user).exists()
    print(f'Username: {user.username}, Email: {user.email}, Has Profile: {has_profile}')
"
        ;;
    create_superuser)
        echo "Creating superuser..."
        $MANAGE_CMD createsuperuser
        ;;
    change_superuser_email)
        if [ -z "$2" ]; then
            echo "Error: New email address is required"
            echo "Usage: $0 change_superuser_email <new_email>"
            exit 1
        fi
        echo "Changing superuser email..."
        $MANAGE_CMD change_superuser_email "$2"
        ;;
    update_superuser_password)
        if [ -z "$2" ]; then
            echo "Error: New password is required"
            echo "Usage: $0 update_superuser_password <new_password>"
            exit 1
        fi
        echo "Updating superuser password..."
        $MANAGE_CMD shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
superuser = User.objects.filter(is_superuser=True).first()
if superuser:
    superuser.set_password('$2')
    superuser.save()
    print('Superuser password updated successfully')
else:
    print('No superuser found')
"
        ;;
    *)
        echo "Usage: $0 {create_profiles|list_users|create_superuser|change_superuser_email|update_superuser_password}"
        exit 1
        ;;
esac

exit 0 