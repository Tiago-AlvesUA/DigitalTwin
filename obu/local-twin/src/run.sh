#!/bin/bash

sudo apt-get update
sudo apt-get install -y libcairo2-dev python3-venv

python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
#python3 local-twin.py