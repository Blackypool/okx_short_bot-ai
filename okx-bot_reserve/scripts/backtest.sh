#!/bin/bash
cd $(dirname $0)/..
source venv/bin/activate
START=${1:-2024-11-01}
END=${2:-2024-12-01}
echo "📊 Running backtest: $START → $END"
python src/main.py --backtest --backtest-start $START --backtest-end $END
