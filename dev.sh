#!/bin/bash

# Activate virtual environment
source venv/bin/activate

# Install/update dependencies
pip install -r requirements.txt
npm install

# Build Tailwind CSS
npm run build:prod

# Collect static files
python manage.py collectstatic --noinput

# Run database migrations
python manage.py migrate

# Start Django development server
python manage.py runserver 0.0.0.0:8000 