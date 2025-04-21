#!/bin/bash

# Script to perform maintenance tasks
# Usage: ./maintenance.sh [migrate|backup|restore]

VENV_PATH="/home/kleber/smdr/venv"
PROJECT_PATH="/home/kleber/smdr"
MANAGE_CMD="$VENV_PATH/bin/python $PROJECT_PATH/manage.py"
BACKUP_DIR="$PROJECT_PATH/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# Activate virtual environment
source $VENV_PATH/bin/activate

# Function to stop all services
stop_services() {
    echo "Stopping all services..."
    
    # Stop Gunicorn
    if [ -f /run/gunicorn.pid ]; then
        kill -TERM $(cat /run/gunicorn.pid)
        rm -f /run/gunicorn.pid
    else
        pkill -f gunicorn
    fi
    
    # Stop any running Django development server
    pkill -f "python manage.py runserver"
    
    # Wait for services to stop
    sleep 2
}

# Function to start services
start_services() {
    echo "Starting services..."
    $PROJECT_PATH/scripts/manage_gunicorn.sh start
}

case "$1" in
    migrate)
        stop_services
        echo "Applying database migrations..."
        $MANAGE_CMD migrate
        start_services
        ;;
    backup)
        stop_services
        echo "Creating database backup..."
        mkdir -p $BACKUP_DIR
        pg_dump -U kleber smdr > "$BACKUP_DIR/smdr_backup_$DATE.sql"
        echo "Backup created: $BACKUP_DIR/smdr_backup_$DATE.sql"
        start_services
        ;;
    restore)
        if [ -z "$2" ]; then
            echo "Please specify backup file to restore"
            echo "Usage: $0 restore <backup_file>"
            exit 1
        fi
        stop_services
        echo "Restoring database from backup..."
        psql -U kleber smdr < "$2"
        start_services
        ;;
    *)
        echo "Usage: $0 {migrate|backup|restore}"
        exit 1
        ;;
esac

exit 0 