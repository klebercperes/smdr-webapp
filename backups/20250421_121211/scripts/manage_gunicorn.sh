#!/bin/bash

# Script to manage Gunicorn service
# Usage: ./manage_gunicorn.sh [start|stop|restart|status]

VENV_PATH="/home/kleber/smdr/venv"
PROJECT_PATH="/home/kleber/smdr"
GUNICORN_CMD="$VENV_PATH/bin/gunicorn"
WSGI_APP="smdrproject.wsgi:application"
PID_FILE="$PROJECT_PATH/gunicorn.pid"
LOG_FILE="$PROJECT_PATH/logs/gunicorn.log"
BIND_ADDRESS="127.0.0.1:8000"

# Create log directory if it doesn't exist
mkdir -p "$PROJECT_PATH/logs"
chmod 755 "$PROJECT_PATH/logs"

case "$1" in
    start)
        echo "Starting Gunicorn..."
        $GUNICORN_CMD $WSGI_APP \
            --workers 3 \
            --bind $BIND_ADDRESS \
            --pid $PID_FILE \
            --access-logfile - \
            --error-logfile $LOG_FILE \
            --daemon
        ;;
    stop)
        echo "Stopping Gunicorn..."
        if [ -f $PID_FILE ]; then
            kill -TERM $(cat $PID_FILE)
            rm -f $PID_FILE
        else
            echo "No PID file found. Trying to find and kill Gunicorn processes..."
            pkill -f gunicorn
        fi
        ;;
    restart)
        echo "Restarting Gunicorn..."
        $0 stop
        sleep 2
        $0 start
        ;;
    status)
        if [ -f $PID_FILE ]; then
            PID=$(cat $PID_FILE)
            if ps -p $PID > /dev/null; then
                echo "Gunicorn is running (PID: $PID)"
            else
                echo "Gunicorn is not running"
            fi
        else
            echo "Gunicorn is not running"
        fi
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status}"
        exit 1
        ;;
esac

exit 0 