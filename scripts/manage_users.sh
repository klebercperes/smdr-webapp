#!/bin/bash

# Script to manage users and profiles
# Usage: ./manage_users.sh [create_profiles|list_users|create_superuser]

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
    *)
        echo "Usage: $0 {create_profiles|list_users|create_superuser}"
        exit 1
        ;;
esac

exit 0 