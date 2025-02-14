#!/bin/bash
export DISPLAY=:0
export XAUTHORITY=/home/rpiirc3/.Xauthority
export PYTHONPATH="${PYTHONPATH}:/usr/lib/python3/dist-packages"

cd /home/rpiirc3/IRC081
source venv/bin/activate
python3 Interface.py
