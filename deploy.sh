#!/bin/bash

# Ufas1Forms Deployment Script
# This script deploys the project using uvicorn and sets it up as a systemd service
# NOTE: This script requires sudo privileges to install the systemd service and manage the system

set -e  # Exit immediately if a command exits with a non-zero status

echo "Starting Ufas1Forms deployment with uvicorn..."

# Check if running with sudo privileges
if [[ $EUID -eq 0 ]]; then
    echo "Running as root user"
else
    echo "This script requires sudo privileges to install systemd service and manage system services"
    echo "Please run with: sudo ./deploy.sh"
    exit 1
fi

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Create destination directory if it doesn't exist
DEPLOY_DIR="/opt/ufas1forms"
mkdir -p $DEPLOY_DIR

# Copy project files to destination (excluding .git, venv, and other unnecessary files)
echo "Copying project files to $DEPLOY_DIR..."
rsync -av \
    --exclude='.git' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='.gitignore' \
    --exclude='QWEN.md' \
    --exclude='deploy.sh' \
    ./ $DEPLOY_DIR/

# Change DEBUG from True to False in production settings
echo "Updating settings for production (DEBUG=False)..."
sed -i 's/DEBUG = True/DEBUG = False/' $DEPLOY_DIR/ufas1forms/settings.py

# Copy the virtual environment
if [ -d "venv" ]; then
    echo "Copying virtual environment to production..."
    rsync -av venv/ $DEPLOY_DIR/venv/
else
    echo "Creating and setting up virtual environment in production..."
    python3 -m venv $DEPLOY_DIR/venv
    $DEPLOY_DIR/venv/bin/pip install --upgrade pip
    $DEPLOY_DIR/venv/bin/pip install -r $DEPLOY_DIR/requirements.txt
fi

# Collect static files
echo "Collecting static files..."
cd $DEPLOY_DIR
source venv/bin/activate
python manage.py collectstatic --noinput


# Set appropriate permissions
echo "Setting file permissions..."
chmod -R 775 $DEPLOY_DIR
chmod 664 $DEPLOY_DIR/db.sqlite3

# Ensure media directory has proper permissions for web access
if [ -d "$DEPLOY_DIR/media" ]; then
    chmod -R 755 $DEPLOY_DIR/media
    find $DEPLOY_DIR/media -type f -exec chmod 644 {} \;
fi


sudo systemctl restart ufas1forms.service
sudo systemctl status ufas1forms.service 