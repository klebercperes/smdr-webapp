#!/bin/bash

# Script to manage production tasks
# Usage: ./manage_prod.sh [restart|reload|status|logs|build|migrate|backup_db]

VENV_PATH="/home/kleber/smdr/venv"
PROJECT_PATH="/home/kleber/smdr"
MANAGE_CMD="$VENV_PATH/bin/python $PROJECT_PATH/manage.py"
BACKUP_DIR="$PROJECT_PATH/backups"
KEEP_BACKUPS=2

# Load environment variables
if [ -f "$PROJECT_PATH/.env" ]; then
    export $(grep -v '^#' "$PROJECT_PATH/.env" | xargs)
fi

# Get database credentials from Django settings
DB_NAME="smdrdb"  # Hardcoded since we know the correct database name
DB_USER=$(python3 -c "
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smdrproject.settings')
from django.conf import settings
print(settings.DATABASES['default']['USER'])
")
DB_PASSWORD=$(python3 -c "
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smdrproject.settings')
from django.conf import settings
print(settings.DATABASES['default']['PASSWORD'])
")
DB_HOST=$(python3 -c "
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smdrproject.settings')
from django.conf import settings
print(settings.DATABASES['default']['HOST'])
")
DB_PORT=$(python3 -c "
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smdrproject.settings')
from django.conf import settings
print(settings.DATABASES['default']['PORT'])
")

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

# Function to verify backup
verify_backup() {
    local backup_file=$1
    echo "Verifying backup file: $backup_file"
    
    # Check if file exists and is not empty
    if [ ! -s "$backup_file" ]; then
        echo "Error: Backup file is empty or does not exist"
        return 1
    fi
    
    # Check if it's a valid gzip file
    if ! gzip -t "$backup_file"; then
        echo "Error: Backup file is corrupted"
        return 1
    fi
    
    # Test restore to a temporary database
    echo "Testing restore to temporary database..."
    TEMP_DB="smdrdb_backup_test_$(date +%s)"
    PGPASSWORD=$DB_PASSWORD createdb -h $DB_HOST -p $DB_PORT -U $DB_USER "$TEMP_DB"
    if ! PGPASSWORD=$DB_PASSWORD gunzip -c "$backup_file" | psql -h $DB_HOST -p $DB_PORT -U $DB_USER "$TEMP_DB" > /dev/null 2>&1; then
        echo "Error: Backup restore test failed"
        PGPASSWORD=$DB_PASSWORD dropdb -h $DB_HOST -p $DB_PORT -U $DB_USER "$TEMP_DB"
        return 1
    fi
    PGPASSWORD=$DB_PASSWORD dropdb -h $DB_HOST -p $DB_PORT -U $DB_USER "$TEMP_DB"
    echo "Backup verification successful"
    return 0
}

# Function to rotate backups
rotate_backups() {
    echo "Rotating backups, keeping last $KEEP_BACKUPS backups..."
    # List all backup files, sort by modification time (newest first)
    local backups=($(ls -t "$BACKUP_DIR"/db_backup_*.sql.gz))
    local count=${#backups[@]}
    
    # Remove old backups if we have more than KEEP_BACKUPS
    if [ $count -gt $KEEP_BACKUPS ]; then
        for ((i=KEEP_BACKUPS; i<count; i++)); do
            echo "Removing old backup: ${backups[$i]}"
            rm "${backups[$i]}"
        done
    fi
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
    backup_db)
        echo "Starting database backup process..."
        TIMESTAMP=$(date +%Y%m%d_%H%M%S)
        BACKUP_FILE="$BACKUP_DIR/db_backup_$TIMESTAMP.sql"
        COMPRESSED_FILE="$BACKUP_FILE.gz"
        
        # Create backup
        echo "Creating database backup..."
        if ! PGPASSWORD=$DB_PASSWORD pg_dump -h $DB_HOST -p $DB_PORT -U $DB_USER $DB_NAME > "$BACKUP_FILE"; then
            echo "Error: Database backup failed"
            exit 1
        fi
        
        # Compress backup
        echo "Compressing backup..."
        if ! gzip "$BACKUP_FILE"; then
            echo "Error: Backup compression failed"
            exit 1
        fi
        
        # Verify backup
        if ! verify_backup "$COMPRESSED_FILE"; then
            echo "Error: Backup verification failed"
            exit 1
        fi
        
        # Rotate backups
        rotate_backups
        
        echo "Database backup completed successfully:"
        echo "Local backup: $COMPRESSED_FILE"
        echo "To push to GitHub, run:"
        echo "git add -f $COMPRESSED_FILE"
        echo "git commit -m 'Database backup $TIMESTAMP'"
        echo "git push"
        ;;
    *)
        echo "Usage: $0 {restart|reload|status|logs|build|migrate|backup_db}"
        exit 1
        ;;
esac

exit 0 