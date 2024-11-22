#!/bin/bash

# Define variables
REPO_URL="https://github.com/Baumjamin03/IRC081.git"
CLONE_DIR="./IRC081"
DEPENDENCIES="git python3 python3-pip python3-venv python3-tk python3-pil python3-pil.imagetk i2c-tools libjpeg-dev zlib1g-dev libpng-dev libfreetype6-dev plymouth plymouth-themes"
MAIN_SCRIPT="Interface.py"

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

# Main installation process
echo "-----Updating package list and installing dependencies..."
sudo apt update
sudo apt install -y $DEPENDENCIES

echo "-----Cloning the repository..."
if [ -d "$CLONE_DIR" ]; then
    rm -rf "$CLONE_DIR"
fi
git clone -b Interface2.0 $REPO_URL $CLONE_DIR
cd $CLONE_DIR || exit

echo "-----Creating a virtual environment..."
python3 -m venv venv

echo "-----Activating the virtual environment..."
source venv/bin/activate

if [ -f "./Assets/requirements.txt" ]; then
    echo "-----Installing Python dependencies in the virtual environment..."
    pip install -r ./Assets/requirements.txt
fi

echo "-----Creating launcher script..."
create_launcher

echo "-----Creating and enabling systemd service..."
sudo systemctl daemon-reload
sudo systemctl enable irc081.service

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