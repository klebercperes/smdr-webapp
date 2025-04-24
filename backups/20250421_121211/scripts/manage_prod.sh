#!/bin/bash

# Script to manage production tasks
# Usage: ./manage_prod.sh [restart|reload|status|logs|build|migrate]

VENV_PATH="/home/kleber/smdr/venv"
PROJECT_PATH="/home/kleber/smdr"
MANAGE_CMD="$VENV_PATH/bin/python $PROJECT_PATH/manage.py"

# Activate virtual environment
source $VENV_PATH/bin/activate

# Function to check service status
check_status() {
    echo "Checking services status..."
    systemctl status nginx | grep "Active:"
    systemctl status gunicorn | grep "Active:"
}

# Function to view logs
view_logs() {
    echo "Last 50 lines of Nginx error log:"
    sudo tail -n 50 /var/log/nginx/error.log
    echo -e "\nLast 50 lines of Gunicorn log:"
    sudo tail -n 50 /var/log/gunicorn/smdr.log
}

case "$1" in
    restart)
        echo "Restarting services..."
        sudo systemctl restart nginx
        sudo systemctl restart gunicorn
        check_status
        ;;
    reload)
        echo "Restarting services gracefully..."
        sudo systemctl restart nginx
        sudo systemctl restart gunicorn
        check_status
        ;;
    status)
        check_status
        ;;
    logs)
        view_logs
        ;;
    build)
        echo "Building static files..."
        # Build Tailwind CSS
        cd $PROJECT_PATH && npm run build:prod
        # Collect static files
        $MANAGE_CMD collectstatic --noinput --clear
        # Reload Nginx to pick up new static files
        sudo systemctl reload nginx
        ;;
    migrate)
        echo "Applying database migrations..."
        $MANAGE_CMD migrate
        # Restart Gunicorn to pick up model changes
        sudo systemctl restart gunicorn
        ;;
    *)
        echo "Usage: $0 {restart|reload|status|logs|build|migrate}"
        exit 1
        ;;
esac

exit 0 