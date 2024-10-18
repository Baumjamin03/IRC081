#!/bin/bash

# Define variables
REPO_URL="https://github.com/Baumjamin03/IRC081.git"
CLONE_DIR="./IRC081"
UDEV_RULE_FILE="61-mcc.rules"
DEST_UDEV_RULE_FILE="/etc/udev/rules.d"
DEPENDENCIES="git python3 python3-pip python3-venv python3-tk python3-pil python3-pil.imagetk i2c-tools"
MAIN_SCRIPT="IRUI081.py"  # Updated main script name

# Create launcher script
create_launcher() {
    cat > launcher.sh << 'EOL'
#!/bin/bash
sleep 10
export DISPLAY=:0
export XAUTHORITY=/home/pi/.Xauthority
export PYTHONPATH="${PYTHONPATH}:/usr/lib/python3/dist-packages"

cd /home/pi/IRC081
source venv/bin/activate
python3 IRUI081.py
EOL
    chmod +x launcher.sh
}

# Create systemd service
create_service() {
    sudo bash -c 'cat > /etc/systemd/system/irc081.service << EOL
[Unit]
Description=IRC081 Python Application
After=network.target graphical.target

[Service]
Environment=DISPLAY=:0
Environment=XAUTHORITY=/home/pi/.Xauthority
User=pi
Group=pi
ExecStart=/home/pi/IRC081/launcher.sh
Restart=always
RestartSec=10
Type=simple
KillMode=process
TimeoutStopSec=20

[Install]
WantedBy=graphical.target
EOL'
}

# Enable I2C and Serial
configure_interfaces() {
    # Enable I2C
    sudo raspi-config nonint do_i2c 0

    # Enable Serial
    sudo raspi-config nonint do_serial 0

    # Add modules to /etc/modules
    if ! grep -q "i2c-dev" /etc/modules; then
        echo "i2c-dev" | sudo tee -a /etc/modules
    fi
    if ! grep -q "i2c-bcm2708" /etc/modules; then
        echo "i2c-bcm2708" | sudo tee -a /etc/modules
    fi
}

# Main installation process
echo "Updating package list and installing dependencies..."
sudo apt update
sudo apt install -y $DEPENDENCIES

echo "Configuring I2C and Serial interfaces..."
configure_interfaces

echo "Cloning the repository..."
git clone $REPO_URL $CLONE_DIR
cd $CLONE_DIR || exit

echo "Creating a virtual environment..."
python3 -m venv venv

echo "Activating the virtual environment..."
source venv/bin/activate

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

echo "Creating launcher script..."
create_launcher

echo "Creating and enabling systemd service..."
create_service
sudo systemctl daemon-reload
sudo systemctl enable irc081.service

echo "Setting up X server permissions..."
echo "xhost +local:pi" >> ~/.bashrc
xhost +local:pi

echo "Reloading udev rules..."
sudo udevadm control --reload

echo "Installation complete! The application will start automatically on next boot."
echo "To start it now without rebooting, run: sudo systemctl start irc081.service"
echo "To check status: sudo systemctl status irc081.service"

# Verify main script exists
if [ ! -f "$MAIN_SCRIPT" ]; then
    echo "WARNING: $MAIN_SCRIPT not found in repository. Please verify the main script name."
fi

# Offer to reboot
read -p "Would you like to reboot now? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
    sudo reboot
fi