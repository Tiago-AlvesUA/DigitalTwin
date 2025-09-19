#!/bin/bash
set -e

# We assume libcairo2-dev and python3-venv is already installed in the obu image, by running the run script of local-twin

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

nohup python network-delay.py > logs/network-delay.log 2>&1 &
nohup python network-tt.py > logs/network-tt.log 2>&1 &

echo "Both scripts are running in background. Check logs/network-* for output."
