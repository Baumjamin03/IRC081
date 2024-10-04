#!/bin/bash

# Define variables
REPO_URL="https://github.com/Baumjamin03/IRC081.git"
CLONE_DIR="./IRC081"
UDEV_RULE_FILE="61-mcc.rules"  # Name of the udev rules file in the repository
DEST_UDEV_RULE_FILE="/etc/udev/rules.d"
DEPENDENCIES="git python3 python3-pip python3-venv"  # Adding python3-venv to install venv

# Update and install dependencies
echo "Updating package list and installing dependencies..."
sudo apt update
sudo apt install -y $DEPENDENCIES

# Clone the Git repository
echo "Cloning the repository..."
git clone $REPO_URL $CLONE_DIR

# Navigate to the cloned repository directory
cd $CLONE_DIR || exit

# Create a Python virtual environment in the cloned directory
echo "Creating a virtual environment..."
python3 -m venv venv

# Activate the virtual environment
echo "Activating the virtual environment..."
source venv/bin/activate

# Install Python dependencies from requirements.txt into the virtual environment
if [ -f "requirements.txt" ]; then
    echo "Installing Python dependencies in the virtual environment..."
    pip install -r requirements.txt
fi


if [ -f "$UDEV_RULE_FILE" ]; then
    echo "Copying udev rules file to /etc/udev/rules.d/"
    sudo cp "$UDEV_RULE_FILE" "$DEST_UDEV_RULE_FILE"
else
    echo "No udev rules file found in the repository. Skipping udev rule installation."
fi

# Reload udev rules to apply the new rule
echo "Reloading udev rules..."
/sbin/udevadm control --reload

echo "Setup complete! Virtual environment is ready, dependencies are installed, and udev rules have been updated."

# Note: The virtual environment is active within this script, but once the script ends,
#       the user will need to manually activate it in their terminal with:
#       source /home/pi/yourrepo/venv/bin/activate