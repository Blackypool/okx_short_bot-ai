#!/bin/bash
cd $(dirname $0)/..
source venv/bin/activate
echo "⚠️  WARNING: LIVE TRADING MODE - REAL MONEY!"
python src/main.py --mode livetrade
