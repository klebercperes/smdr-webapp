#!/bin/bash

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "Please run as root"
    exit 1
fi

# Set timezone to Australia/Brisbane
echo "Setting timezone to Australia/Brisbane..."
timedatectl set-timezone Australia/Brisbane

# Verify the change
echo "Current timezone:"
timedatectl | grep "Time zone"

# Restart systemd-timesyncd to apply changes
systemctl restart systemd-timesyncd

echo "Timezone has been set to Australia/Brisbane" 