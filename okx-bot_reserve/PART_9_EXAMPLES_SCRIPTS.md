# OKX Intraday Short Bot — PART 9: USAGE EXAMPLES & SCRIPTS

## 📝 PART 9: Practical Examples & Helper Scripts

---

## examples/simple_backtest.py

```python
"""
Simple Backtest Example

Shows how to run backtest on historical data
"""

from src.backtest.backtester import Backtester
from src.utils.config_loader import ConfigLoader

# Load configuration
config = ConfigLoader("config").load()

# Create backtester
backtester = Backtester(
    config=config,
    start_date="2024-11-01",
    end_date="2024-11-30"
)

# Run backtest
results = backtester.run()

# Print results
print(f"""
Backtest Results
================
Period: {results['start_date']} to {results['end_date']}
Total Trades: {results['total_trades']}
Winning: {results['winning_trades']}
Losing: {results['losing_trades']}
Win Rate: {results['win_rate']:.1f}%
Total P&L: ${results['total_pnl']:.2f}
""")
```

---

## examples/test_signal_generation.py

```python
"""
Test Signal Generation

Shows how to test signal generation logic
"""

import pandas as pd
from src.ta.fvg_detector import FVGDetector
from src.ta.trendlines import TrendlineAnalyzer
from src.ta.trend_state import TrendState
from src.strategy.signal_engine import SignalEngine

# Create sample OHLCV data
data = {
    'open': [100, 101, 99, 100, 101, 102, 101, 103],
    'high': [101, 105, 102, 101, 102, 104, 102, 105],
    'low': [99, 100, 98, 99, 100, 101, 100, 102],
    'close': [100.5, 103, 99.5, 100.5, 101.5, 103.5, 101.5, 104]
}
df_m15 = pd.DataFrame(data)
df_h1 = pd.DataFrame(data)

# Initialize analyzers
fvg_detector = FVGDetector()
trendline_analyzer = TrendlineAnalyzer()
trend_state = TrendState()
signal_engine = SignalEngine()

# Analyze
is_uptrend, trend_info = trend_state.is_uptrend(df_m15)
fvgs = fvg_detector.detect_fvg(df_m15)
minima = trendline_analyzer.find_local_minima(df_m15)
trendline = trendline_analyzer.build_trendline(minima) if minima else None

# Generate signals
analysis = {
    'is_uptrend': is_uptrend,
    'fvgs': fvgs,
    'trendline': trendline
}

signals = signal_engine.generate_signals("BTC-USDT", df_m15, df_h1, analysis)

# Print signals
for signal in signals:
    print(f"Signal: {signal['type']} - Confidence: {signal['confidence']}%")
```

---

## examples/paper_trading.py

```python
"""
Paper Trading Example

Shows how to use the paper trading simulator
"""

from src.backtest.simulator import PaperTradingSimulator

# Create simulator with $1000 starting balance
simulator = PaperTradingSimulator(initial_balance=1000.0)

# Simulate opening position
print("Opening short position...")
simulator.open_position(
    symbol="BTC-USDT",
    side="sell",
    entry_price=100.0,
    size=0.1,
    tp=95.0,      # Target 5 points profit
    sl=102.0      # Stop loss 2 points
)

# Simulate closing position
print("Closing position...")
trade_result = simulator.close_position("BTC-USDT", exit_price=95.5)

print(f"""
Trade Result:
Entry: {trade_result['entry']}
Exit: {trade_result['exit']}
Size: {trade_result['size']}
P&L: ${trade_result['pnl']:.2f}
P&L %: {trade_result['pnl_pct']:.2f}%
""")

# Print simulator status
status = simulator.get_status()
print(f"""
Simulator Status:
Equity: ${status['equity']:.2f}
Open Positions: {status['open_positions']}
Total Trades: {status['total_trades']}
Total P&L: ${status['total_pnl']:.2f}
""")
```

---

## examples/risk_calculation.py

```python
"""
Risk & Position Sizing Example

Shows how to calculate R/R and position size
"""

from src.strategy.rr_calculator import RRCalculator
from src.strategy.risk_manager import RiskManager

# Initialize calculator
calc = RRCalculator()

# Example trade setup
entry_price = 100.0
stop_price = 98.0
tp_price = 110.0
deposit = 1000.0

# Calculate R/R
rr = calc.calculate_rr(entry_price, stop_price, tp_price)
print(f"Risk/Reward Ratio: 1:{rr}")

# Calculate position size
position_size = calc.calculate_position_size(
    entry_price=entry_price,
    stop_price=stop_price,
    deposit=deposit,
    leverage=10,
    max_risk_pct=5.0
)
print(f"Position Size: {position_size:.4f} contracts")

# Calculate risk amount
risk_distance = abs(entry_price - stop_price)
risk_amount = risk_distance * position_size
risk_pct = (risk_amount / deposit) * 100

print(f"""
Position Sizing:
Entry: ${entry_price}
Stop: ${stop_price}
Risk per contract: ${risk_distance}
Position size: {position_size:.4f}
Total risk: ${risk_amount:.2f}
Risk %: {risk_pct:.2f}%
""")

# Validate
is_valid_rr = calc.validate_rr(rr, min_rr=4.0)
print(f"Valid R/R (>= 1:4): {is_valid_rr}")
```

---

## examples/correlation_analysis.py

```python
"""
BTC Correlation Analysis Example

Shows how to check correlation filtering
"""

from src.data.correlation import CorrelationAnalyzer
from src.data.market_data import MarketDataManager
from src.api.okx_client import OKXClient
import os

# Setup
api_key = os.getenv("OKX_API_KEY")
api_secret = os.getenv("OKX_API_SECRET")
passphrase = os.getenv("OKX_PASSPHRASE")

# Initialize
config = {
    'api_key': api_key,
    'api_secret': api_secret,
    'passphrase': passphrase,
    'sandbox': False
}

api_client = OKXClient(config)
market_data = MarketDataManager(api_client)
correlation = CorrelationAnalyzer(market_data)

# Calculate correlation for multiple symbols
symbols = ["BTC-USDT", "ETH-USDT", "SOL-USDT", "XRP-USDT"]

print("24-hour BTC Correlation Analysis:")
print("-" * 40)

for symbol in symbols:
    corr = correlation.calculate_correlation_24h(symbol)
    status = "✓ PASS" if abs(corr) <= 0.2 else "✗ FAIL"
    print(f"{symbol}: {corr:.3f} {status}")
```

---

## scripts/run_signal_only.sh

```bash
#!/bin/bash
# Start bot in signal-only mode (safe for testing)

cd "$(dirname "$0")/.."

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3.10 -m venv venv
fi

# Activate venv
source venv/bin/activate

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "ERROR: .env file not found!"
    echo "Please copy .env.example to .env and fill with credentials"
    exit 1
fi

# Run in signal-only mode
echo "Starting bot in SIGNAL-ONLY mode..."
echo "Logs: tail -f logs/app.log"
echo "Ctrl+C to stop"

python src/main.py --mode signal_only --verbose
```

---

## scripts/run_live.sh

```bash
#!/bin/bash
# Start bot in live trading mode (REAL MONEY!)

cd "$(dirname "$0")/.."

# Safety check
echo "⚠️  WARNING: About to start LIVE TRADING with REAL MONEY!"
echo "⚠️  Have you:"
echo "  1. Tested in signal_only mode for 3-5 days? (y/n)"
read -r tested

if [ "$tested" != "y" ]; then
    echo "Please test in signal_only mode first!"
    exit 1
fi

echo "  2. Verified all configuration in config/*.yaml? (y/n)"
read -r verified

if [ "$verified" != "y" ]; then
    echo "Please verify configuration first!"
    exit 1
fi

echo "  3. Read the DISCLAIMER and understand the risks? (y/n)"
read -r understood

if [ "$understood" != "y" ]; then
    echo "Please read and understand the risks!"
    exit 1
fi

# Activate venv
source venv/bin/activate

# Run in live mode
echo "Starting bot in LIVE-TRADE mode..."
echo "Monitor carefully! Logs: tail -f logs/app.log"
echo "Emergency stop: Ctrl+C"

python src/main.py --mode live_trade
```

---

## scripts/backtest.sh

```bash
#!/bin/bash
# Run backtest on historical data

cd "$(dirname "$0")/.."

# Activate venv
source venv/bin/activate

# Get dates
if [ -z "$1" ] || [ -z "$2" ]; then
    echo "Usage: ./scripts/backtest.sh START_DATE END_DATE"
    echo "Example: ./scripts/backtest.sh 2024-11-01 2024-11-30"
    exit 1
fi

START_DATE=$1
END_DATE=$2

echo "Running backtest from $START_DATE to $END_DATE..."

python src/main.py \
    --backtest \
    --backtest-start "$START_DATE" \
    --backtest-end "$END_DATE" \
    --verbose

echo "Backtest complete! Check reports/pdf/ for results"
```

---

## scripts/generate_report.sh

```bash
#!/bin/bash
# Generate daily report

cd "$(dirname "$0")/.."

# Activate venv
source venv/bin/activate

DATE=$(date +%Y-%m-%d)

echo "Generating report for $DATE..."

python -c "
from src.reporting.logger import TradeLogger
from src.reporting.latex_reporter import LaTeXReporter

logger = TradeLogger()
stats = logger.get_daily_stats('$DATE')

reporter = LaTeXReporter()
tex_file = reporter.generate_daily_report('$DATE', logger.get_today_trades())

print(f'Report generated: {tex_file}')
print('Compiling to PDF...')

pdf_file = reporter.compile_to_pdf(tex_file)
print(f'PDF: {pdf_file}')
"
```

---

## scripts/monitor.sh

```bash
#!/bin/bash
# Real-time monitoring script

cd "$(dirname "$0")/.."

echo "OKX Short Bot - Live Monitoring"
echo "================================"
echo ""
echo "App Log:"
echo "--------"

# Watch app log
tail -f logs/app.log &
LOG_PID=$!

# Watch trades
watch -n 5 "
    echo ''
    echo 'Today's Trades:'
    echo '---------------'
    [ -f logs/trades_\$(date +%Y%m%d).json ] && cat logs/trades_\$(date +%Y%m%d).json | python -m json.tool | tail -20
" &

WATCH_PID=$!

# Cleanup on exit
trap "kill $LOG_PID $WATCH_PID" EXIT

wait
```

---

## scripts/test_api.sh

```bash
#!/bin/bash
# Test OKX API connection

cd "$(dirname "$0")/.."

# Activate venv
source venv/bin/activate

echo "Testing OKX API connection..."

python -c "
import os
from src.api.okx_client import OKXClient

config = {
    'api_key': os.getenv('OKX_API_KEY'),
    'api_secret': os.getenv('OKX_API_SECRET'),
    'passphrase': os.getenv('OKX_PASSPHRASE'),
    'sandbox': True  # Use sandbox
}

client = OKXClient(config)

try:
    balance = client.get_account_balance()
    print('✓ API Connection: SUCCESS')
    print(f'  Account Balance: \${balance}')
    
    contracts = client.get_futures_contracts()
    print(f'✓ Contracts Retrieved: {len(contracts)} contracts found')
    
except Exception as e:
    print(f'✗ API Connection: FAILED')
    print(f'  Error: {e}')
"
```

---

## scripts/run_tests.sh

```bash
#!/bin/bash
# Run all unit tests

cd "$(dirname "$0")/.."

# Activate venv
source venv/bin/activate

echo "Running unit tests..."

python -m pytest tests/ -v --cov=src --cov-report=html

echo ""
echo "Test results saved to htmlcov/index.html"
```

---

## scripts/cleanup.sh

```bash
#!/bin/bash
# Clean up temporary files

cd "$(dirname "$0")/.."

echo "Cleaning up..."

# Remove cache
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete

# Remove old logs (keep 30 days)
find logs -type f -mtime +30 -delete

# Remove old data
find data/historical -type f -mtime +90 -delete

# Remove test cache
rm -rf .pytest_cache
rm -rf .coverage
rm -rf htmlcov

echo "Cleanup complete!"
```

---

## Makefile

```makefile
.PHONY: help setup test run-signal run-live backtest clean monitor

help:
	@echo "OKX Short Bot - Commands"
	@echo "======================="
	@echo "make setup          - Setup virtual environment"
	@echo "make test           - Run unit tests"
	@echo "make run-signal     - Run in signal-only mode (safe)"
	@echo "make run-live       - Run in live trading mode (REAL MONEY!)"
	@echo "make backtest       - Run backtest"
	@echo "make monitor        - Monitor running bot"
	@echo "make clean          - Clean up temporary files"

setup:
	python3.10 -m venv venv
	. venv/bin/activate && pip install -r requirements.txt
	cp .env.example .env
	@echo "Setup complete! Edit .env with your credentials"

test:
	. venv/bin/activate && python -m pytest tests/ -v

run-signal:
	. venv/bin/activate && python src/main.py --mode signal_only --verbose

run-live:
	. venv/bin/activate && python src/main.py --mode live_trade

backtest:
	@echo "Usage: make backtest START_DATE=2024-11-01 END_DATE=2024-11-30"
	. venv/bin/activate && python src/main.py --backtest --backtest-start $(START_DATE) --backtest-end $(END_DATE)

monitor:
	tail -f logs/app.log

clean:
	bash scripts/cleanup.sh

install-dev:
	. venv/bin/activate && pip install -e ".[dev]"
	. venv/bin/activate && pre-commit install
```

---

**PART 9 Готова:**

✅ examples/simple_backtest.py
✅ examples/test_signal_generation.py
✅ examples/paper_trading.py
✅ examples/risk_calculation.py
✅ examples/correlation_analysis.py
✅ scripts/run_signal_only.sh
✅ scripts/run_live.sh
✅ scripts/backtest.sh
✅ scripts/generate_report.sh
✅ scripts/monitor.sh
✅ scripts/test_api.sh
✅ scripts/run_tests.sh
✅ scripts/cleanup.sh
✅ Makefile

Готов к PART 10 (финальные файлы, документация, чек-листы)?
