#!/bin/bash

# Make sure we're in the project root
cd "$(dirname "$0")/.."

echo "Starting cleanup process..."

# Remove Python cache files
find . -type d -name "__pycache__" -exec rm -r {} +
find . -type f -name "*.pyc" -delete
find . -type f -name "*.pyo" -delete
find . -type f -name "*.pyd" -delete

# Remove Node.js cache and build files
rm -rf node_modules/
rm -rf .npm/
rm -rf dist/
rm -rf build/

# Remove development-specific files
rm -f .env.local
rm -f .env.development
rm -f .env.test

# Remove IDE-specific files
rm -rf .idea/
rm -rf .vscode/
rm -f *.swp
rm -f *.swo

# Remove temporary files
rm -rf tmp/
rm -rf temp/

# Clean up static files (they will be regenerated)
rm -rf staticfiles/
mkdir -p staticfiles

# Clean up media files (if needed)
# rm -rf media/
# mkdir -p media

echo "Cleanup completed. Please run the following commands to rebuild:"
echo "1. pip install -r requirements.txt"
echo "2. npm install"
echo "3. npm run build:prod"
echo "4. python manage.py collectstatic --noinput" 