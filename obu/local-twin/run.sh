#!/bin/bash

sudo apt-get update
sudo apt-get install -y libcairo2-dev python3-venv

python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python local-twin.py