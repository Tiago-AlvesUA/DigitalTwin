#!/bin/bash
set -e

# We assume libcairo2-dev and python3-venv is already installed in the obu image, by running the run script of local-twin

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# python3 network-delay.py
# python3 network-tt.py

#echo "Both scripts are running in background. Check logs/network-* for output."
