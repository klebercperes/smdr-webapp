#!/bin/bash

# Script to start all servers after reboot
# Usage: ./start_servers.sh

VENV_PATH="/home/kleber/smdr/venv"
PROJECT_PATH="/home/kleber/smdr"
GUNICORN_CONFIG="$PROJECT_PATH/gunicorn_config.py"
LOG_FILE="/var/log/smdr/server_start.log"

# Function to log messages
log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a $LOG_FILE
}

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    log_message "Error: This script must be run as root"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "$VENV_PATH" ]; then
    log_message "Error: Virtual environment not found at $VENV_PATH"
    exit 1
fi

# Check if project directory exists
if [ ! -d "$PROJECT_PATH" ]; then
    log_message "Error: Project directory not found at $PROJECT_PATH"
    exit 1
fi

# Check if gunicorn config exists
if [ ! -f "$GUNICORN_CONFIG" ]; then
    log_message "Error: Gunicorn config not found at $GUNICORN_CONFIG"
    exit 1
fi

# Create log directory if it doesn't exist
mkdir -p $(dirname $LOG_FILE)
touch $LOG_FILE

log_message "Starting server initialization..."

# Activate virtual environment
source $VENV_PATH/bin/activate
if [ $? -ne 0 ]; then
    log_message "Error: Failed to activate virtual environment"
    exit 1
fi

# Check if nginx is installed
if ! command -v nginx &> /dev/null; then
    log_message "Error: nginx is not installed"
    exit 1
fi

# Start nginx
log_message "Starting nginx..."
if ! systemctl is-active --quiet nginx; then
    systemctl start nginx
    if [ $? -ne 0 ]; then
        log_message "Error: Failed to start nginx"
        systemctl status nginx | tee -a $LOG_FILE
        exit 1
    fi
    log_message "Nginx started successfully"
else
    log_message "Nginx is already running"
fi

# Check if gunicorn is installed in venv
if [ ! -f "$VENV_PATH/bin/gunicorn" ]; then
    log_message "Error: gunicorn is not installed in virtual environment"
    exit 1
fi

# Start gunicorn
log_message "Starting gunicorn..."
cd $PROJECT_PATH
if ! pgrep -f "gunicorn.*smdr.wsgi:application" > /dev/null; then
    $VENV_PATH/bin/gunicorn -c $GUNICORN_CONFIG smdr.wsgi:application &
    if [ $? -ne 0 ]; then
        log_message "Error: Failed to start gunicorn"
        exit 1
    fi
    log_message "Gunicorn started successfully"
else
    log_message "Gunicorn is already running"
fi

# Verify Django is running
log_message "Verifying Django is running..."
for i in {1..5}; do
    if curl -s http://localhost:8000/health/ > /dev/null; then
        log_message "Django is running successfully"
        break
    fi
    if [ $i -eq 5 ]; then
        log_message "Error: Failed to verify Django is running after 5 attempts"
        exit 1
    fi
    sleep 2
    log_message "Attempt $i: Waiting for Django to start..."
done

log_message "All servers started successfully!"
exit 0 