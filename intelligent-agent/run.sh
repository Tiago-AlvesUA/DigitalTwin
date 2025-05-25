#!/bin/bash

python3 -m venv venv-name
source venv-name/bin/activate
pip install -r ./requirements.txt
python3 src/agent.py
