#!/bin/bash

# Script to manage development tasks
# Usage: ./manage_dev.sh [start|stop|runserver|migrate|shell|createsuperuser|build|setup]

VENV_PATH="/home/kleber/smdr/venv"
PROJECT_PATH="/home/kleber/smdr"
MANAGE_CMD="$VENV_PATH/bin/python $PROJECT_PATH/manage.py"

# Activate virtual environment
source $VENV_PATH/bin/activate

# Function to stop the development server
stop_server() {
    echo "Stopping development server..."
    # Find the process ID using port 8000
    PID=$(lsof -t -i:8000)
    if [ ! -z "$PID" ]; then
        echo "Found process $PID using port 8000"
        # Kill the process
        kill -9 $PID
        # Wait for the process to be killed
        sleep 1
        # Verify the process is gone
        if ps -p $PID > /dev/null; then
            echo "Failed to kill process $PID"
            exit 1
        else
            echo "Successfully stopped process $PID"
        fi
    else
        echo "No process found using port 8000"
    fi
}

case "$1" in
    start)
        echo "Building Tailwind CSS for production..."
        cd $PROJECT_PATH && npm run build:prod
        echo "Collecting static files..."
        $MANAGE_CMD collectstatic --noinput --clear
        echo "Applying any pending migrations..."
        $MANAGE_CMD migrate
        echo "Starting production server..."
        if [ -f /etc/systemd/system/gunicorn.service ]; then
            sudo systemctl restart gunicorn
            sudo systemctl restart nginx
            echo "Production server started. Services restarted."
        else
            echo "Production services not found. Starting development server..."
            stop_server
            $MANAGE_CMD runserver 0.0.0.0:8000
        fi
        ;;
    stop)
        stop_server
        ;;
    runserver)
        stop_server
        echo "Starting development server..."
        $MANAGE_CMD runserver 0.0.0.0:8000
        ;;
    migrate)
        echo "Applying database migrations..."
        $MANAGE_CMD migrate
        ;;
    makemigrations)
        echo "Creating new migrations..."
        $MANAGE_CMD makemigrations
        ;;
    shell)
        echo "Starting Django shell..."
        $MANAGE_CMD shell
        ;;
    createsuperuser)
        echo "Creating superuser..."
        $MANAGE_CMD createsuperuser
        ;;
    build)
        echo "Building Tailwind CSS..."
        cd $PROJECT_PATH && npm run build:prod
        echo "Collecting static files..."
        $MANAGE_CMD collectstatic --noinput --clear
        ;;
    setup)
        echo "Setting up environment..."
        echo "Installing Python dependencies..."
        pip install -r $PROJECT_PATH/requirements.txt
        echo "Installing Node.js dependencies..."
        cd $PROJECT_PATH && npm install
        echo "Building Tailwind CSS..."
        npm run build:prod
        echo "Collecting static files..."
        $MANAGE_CMD collectstatic --noinput --clear
        echo "Applying database migrations..."
        $MANAGE_CMD migrate
        ;;
    *)
        echo "Usage: $0 {start|stop|runserver|migrate|makemigrations|shell|createsuperuser|build|setup}"
        exit 1
        ;;
esac

exit 0 