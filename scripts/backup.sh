#!/bin/bash

# Set timezone to Australia/Brisbane
export TZ=Australia/Brisbane

# Create backup directory with timestamp
BACKUP_DIR="backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

# Backup important directories and files
echo "Creating backup in $BACKUP_DIR..."

# Backup Django project files
cp -r smdrproject "$BACKUP_DIR/"
cp -r smdr "$BACKUP_DIR/"
cp -r staticfiles "$BACKUP_DIR/"
cp -r media "$BACKUP_DIR/"

# Backup configuration files
cp requirements.txt "$BACKUP_DIR/"
cp package.json "$BACKUP_DIR/"
cp tailwind.config.js "$BACKUP_DIR/"
cp postcss.config.js "$BACKUP_DIR/"

# Backup scripts
cp -r scripts "$BACKUP_DIR/"

# Backup database (if you want to include it)
# pg_dump -U your_user your_database > "$BACKUP_DIR/database_backup.sql"

# Create a compressed archive
tar -czf "$BACKUP_DIR.tar.gz" "$BACKUP_DIR"

# Remove the uncompressed backup directory
rm -rf "$BACKUP_DIR"

echo "Backup completed: $BACKUP_DIR.tar.gz" 