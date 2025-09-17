#!/bin/bash

sudo apt install -y python3.10-dev build-essential
python3 -m venv venv-name
source venv-name/bin/activate
pip install -r ./requirements.txt
python3 src/agent.py
