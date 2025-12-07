#!/bin/bash
cd $(dirname $0)/..
source venv/bin/activate
echo "🚀 Starting OKX Bot - SIGNAL-ONLY MODE (SAFE)"
python src/main.py --mode signalonly --verbose
