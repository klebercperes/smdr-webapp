#!/bin/bash

# Script to manage static files
# Usage: ./manage_static.sh [collect|clean]

VENV_PATH="/home/kleber/smdr/venv"
PROJECT_PATH="/home/kleber/smdr"
MANAGE_CMD="$VENV_PATH/bin/python $PROJECT_PATH/manage.py"

# Activate virtual environment
source $VENV_PATH/bin/activate

case "$1" in
    collect)
        echo "Collecting static files..."
        $MANAGE_CMD collectstatic --noinput
        ;;
    clean)
        echo "Cleaning static files..."
        rm -rf $PROJECT_PATH/staticfiles/*
        ;;
    *)
        echo "Usage: $0 {collect|clean}"
        exit 1
        ;;
esac

exit 0 