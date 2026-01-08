#!/bin/bash

echo "--- GHOSTSHIELD INSTALLER ---"
echo ">>> Updating System..."
sudo apt-get update && sudo apt-get install -y python3-pip

echo ">>> Installing Python Dependencies..."
pip3 install -r requirements.txt

# Systemd-resolved stoppen, da es Port 53 blockiert (Problem bei Ubuntu/Raspbian)
echo ">>> Freeing up Port 53..."
sudo systemctl stop systemd-resolved
sudo systemctl disable systemd-resolved

echo ">>> Installation Complete!"
echo ">>> Start GhostShield with: sudo python3 src/main.py"
