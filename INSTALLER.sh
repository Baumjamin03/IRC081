#!/bin/bash

# Define variables
REPO_URL="https://github.com/Baumjamin03/IRC081.git"
CLONE_DIR="./IRC081"
UDEV_RULE_FILE="Assets/61-mcc.rules"
DEST_UDEV_RULE_FILE="/etc/udev/rules.d"
DEPENDENCIES="git python3 python3-pip python3-venv python3-tk python3-pil python3-pil.imagetk i2c-tools libjpeg-dev zlib1g-dev libpng-dev libfreetype6-dev plymouth plymouth-themes"
MAIN_SCRIPT="Interface.py"
SPLASH_IMAGE="Pictures/INFICON_InspiredProvenE.PNG"

# Get the current username
USER_NAME=$(whoami)

# Function to set up splash screen
setup_splash_screen() {
    echo "Setting up custom splash screen..."

    # Backup original plymouth theme splash image
    if [ -f "/usr/share/plymouth/themes/raspberrypi/splash.png" ]; then
        sudo cp "/usr/share/plymouth/themes/pix/splash.png" "/usr/share/plymouth/themes/pix/splash.png.bak"
    fi

    # Copy the new splash image
    if [ -f "$SPLASH_IMAGE" ]; then
        sudo cp "$SPLASH_IMAGE" "/usr/share/plymouth/themes/pix/splash.png"
        sudo chmod 644 "/usr/share/plymouth/themes/pix/splash.png"
        echo "Custom splash image installed directly in raspberrypi theme"
    else
        echo "ERROR: Splash image not found at $SPLASH_IMAGE"
        return 1
    fi

    sudo update-initramfs -u
}

# Function to create launcher script
create_launcher() {
    cat > launcher.sh << EOL
#!/bin/bash
export DISPLAY=:0
export XAUTHORITY=/home/$USER_NAME/.Xauthority
export PYTHONPATH="\${PYTHONPATH}:/usr/lib/python3/dist-packages"

cd /home/$USER_NAME/IRC081
source venv/bin/activate
python3 Interface.py
EOL
    chmod +x launcher.sh
}

# Function to create systemd service with dynamic username and logging
create_service() {
    sudo bash -c "cat > /etc/systemd/system/irc081.service << EOL
[Unit]
Description=IRC081 Python Application
After=network.target graphical.target

[Service]
Environment=DISPLAY=:0
Environment=XAUTHORITY=/home/$USER_NAME/.Xauthority
User=$USER_NAME
Group=$USER_NAME
ExecStart=/home/$USER_NAME/IRC081/launcher.sh
Restart=always
RestartSec=10
Type=simple
KillMode=process
TimeoutStopSec=20

[Install]
WantedBy=graphical.target
EOL"
}

# Enable I2C and Serial
configure_interfaces() {
    # Enable I2C
    sudo raspi-config nonint do_i2c 0

    # Enable Serial
    sudo raspi-config nonint do_serial_hw 0
    sudo raspi-config nonint do_serial_cons 1

    # Add modules to /etc/modules
    if ! grep -q "i2c-dev" /etc/modules; then
        echo "i2c-dev" | sudo tee -a /etc/modules
    fi
    if ! grep -q "i2c-bcm2708" /etc/modules; then
        echo "i2c-bcm2708" | sudo tee -a /etc/modules
    fi
}

# Configure quiet boot
configure_quiet_boot() {
    echo "-----Configuring quiet boot..."
    # Modify cmdline.txt to enable quiet boot
    sudo sed -i 's/$/ quiet splash plymouth.ignore-serial-consoles/' /boot/cmdline.txt

    # Disable boot text
    sudo sed -i 's/^#\?disable_splash=.*$/disable_splash=0/' /boot/config.txt
}

# Main installation process
echo "-----Updating package list and installing dependencies..."
sudo apt update
sudo apt install -y $DEPENDENCIES

echo "-----Configuring I2C and Serial interfaces..."
configure_interfaces

echo "-----Cloning the repository..."
if [ -d "$CLONE_DIR" ]; then
    rm -rf "$CLONE_DIR"
fi
git clone -b Interface2.0 $REPO_URL $CLONE_DIR
cd $CLONE_DIR || exit

echo "-----Setting up splash screen..."
setup_splash_screen
configure_quiet_boot

echo "-----Creating a virtual environment..."
python3 -m venv venv

echo "-----Activating the virtual environment..."
source venv/bin/activate

echo "-----Configuring pip to use PyPI only..."
export PIP_INDEX_URL=https://pypi.org/simple

pip install --upgrade pip setuptools wheel

if [ -f "./Assets/requirements.txt" ]; then
    echo "-----Installing Python dependencies in the virtual environment..."
    pip install -r ./Assets/requirements.txt
fi

if [ -f "$UDEV_RULE_FILE" ]; then
    echo "-----Copying udev rules file to /etc/udev/rules.d/"
    sudo cp "$UDEV_RULE_FILE" "$DEST_UDEV_RULE_FILE"
else
    echo "-----No udev rules file found in the repository. Skipping udev rule installation."
fi

echo "-----Creating launcher script..."
create_launcher

echo "-----Creating and enabling systemd service..."
create_service
sudo systemctl daemon-reload
sudo systemctl enable irc081.service

echo "-----Setting up X server permissions..."
echo "xhost +local:$USER_NAME" >> ~/.bashrc
xhost +local:$USER_NAME

echo "-----Reloading udev rules..."
sudo udevadm control --reload

echo "-----Installation complete! The application will start automatically on next boot."
echo "-----To start it now without rebooting, run: sudo systemctl start irc081.service"
echo "-----To check status: sudo systemctl status irc081.service"

# Verify main script exists
if [ ! -f "$MAIN_SCRIPT" ]; then
    echo "--WARNING: $MAIN_SCRIPT not found in repository. Please verify the main script name."
fi

# Offer to reboot
read -p "-Would you like to reboot now? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
    sudo reboot
fi