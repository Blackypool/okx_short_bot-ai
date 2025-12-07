# OKX Intraday Short Bot — PART 8: COMPLETE CONFIG FILES

## ⚙️ PART 8: Complete Configuration Files (Ready to Use)

---

## config/settings.yaml (Complete)

```yaml
################################
# OKX Short Bot - Settings
# Main configuration for bot operation
################################

bot:
  name: "OKX Intraday Short Bot"
  version: "1.0.0"
  mode: "signal_only"              # Change to "live_trade" for real execution
  verbose: true
  log_level: "INFO"                # DEBUG, INFO, WARNING, ERROR, CRITICAL
  update_interval: 60              # Update every 60 seconds

exchange:
  name: "OKX"
  api_key: "${OKX_API_KEY}"        # From .env file
  api_secret: "${OKX_API_SECRET}"  # From .env file
  passphrase: "${OKX_PASSPHRASE}"  # From .env file
  sandbox: false                   # Set true for testing environment
  rest_url: "https://www.okx.com"
  ws_url: "wss://ws.okx.com:8443/ws/v5/public"
  timeout: 30                      # Request timeout in seconds

timezone: "UTC"

database:
  type: "sqlite"
  path: "data/trades.db"
  backup_enabled: true
  backup_interval_hours: 24

monitoring:
  enable_alerts: true
  alert_channels: ["log", "email"]
  email_recipient: "your_email@example.com"
  heartbeat_interval: 300          # Check bot health every 5 min

logging:
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  file_path: "logs/app.log"
  file_size: 10485760              # 10 MB
  backup_count: 5                  # Keep 5 backup logs
```

---

## config/risk.yaml (Complete)

```yaml
################################
# Risk Management Settings
# CRITICAL: Controls all position sizing and risk
################################

position:
  leverage: 10                     # 10× leverage on USDT-margined futures
  max_risk_pct: 5.0                # Max 5% of deposit at risk per trade
  min_rr: 4.0                      # Minimum 1:4 Risk/Reward ratio
  premium_rr: 3.0                  # 1:3 for perfect technical setups
  premium_setup_flags:
    - "perfect_retest"
    - "fvg_trend_combo"
    - "high_confluence"
    - "strong_volume_confirmation"

position_sizing:
  method: "risk_based"             # risk_based or fixed_size
  fixed_size_usd: 100.0            # If using fixed sizing ($)
  scale_with_volatility: true
  volatility_multiplier: 0.8       # Reduce size if volatility high
  min_position_size: 0.001         # Min contracts
  max_position_size: 10.0          # Max contracts per trade

takeprofit:
  mode: "single"                   # single or two_level
  two_level_split: 0.5             # 50% at first TP, 50% at second
  first_tp_multiplier: 1.5         # Close 50% at 1.5× risk
  second_tp_multiplier: 2.5        # Close 50% at 2.5× risk

stoploss:
  buffer_atr_multiplier: 0.1       # Add 10% of ATR(14) for wick protection
  buffer_pct: 0.5                  # Or 0.5% absolute buffer
  use_atr: true                    # Prefer ATR-based buffer
  atr_period: 14                   # ATR calculation period

max_positions:
  total: 5                         # Max 5 open positions simultaneously
  per_asset: 1                     # Max 1 position per asset
  per_exchange: 5                  # Max 5 per exchange

daily_limits:
  max_trades: 20                   # Max 20 trades per day
  max_loss_pct: 10.0               # Stop trading if day loss > 10%
  max_loss_usd: 5000.0             # Or if loss > $5000 USD
  max_daily_trades_per_asset: 2    # Max 2 trades per asset per day

timeout:
  position_lifetime_hours: 24      # Close positions after 24 hours
  position_review_minutes: 5       # Review every 5 minutes

emergency:
  correlation_spike_threshold: 0.5 # Close if |ρ| > 0.5
  correlation_check_interval: 5    # Check every 5 minutes
  news_event_stop: true            # Stop during news windows
  max_consecutive_losses: 3        # Close all after 3 losses in row
  max_consecutive_losses_action: "stop"  # stop or reduce_size

sl_triggering:
  strict_stop_loss: true           # Enforce exact SL placement
  trailing_stop: false             # Don't use trailing stops
  breakeven_protection: false      # Don't move SL to breakeven

leverage_management:
  dynamic_leverage: false          # Don't adjust leverage
  leverage_per_signal_type:
    FVG_TREND_COMBO: 10            # Full leverage for strongest setup
    FVG_ONLY: 8                    # Reduced for FVG-only
    TREND_ONLY: 8                  # Reduced for trend-only
```

---

## config/filters.yaml (Complete)

```yaml
################################
# Asset Screening & Filtering
# Controls which contracts can be traded
################################

universe:
  # Age filter
  min_age_days: 0                  # No minimum age
  max_age_days: 730                # Max 2 years old (newer, higher momentum)

  # Volume filter
  min_volume_usd: 25000000         # Min $25M 24h volume for liquidity

  # Status filter
  exclude_delisting: true          # Skip contracts being delisted
  exclude_settlement: true         # Skip settlement contracts
  exclude_suspended: true          # Skip suspended contracts
  exclude_testnet: true            # Skip testnet instruments

  # Preferred asset types
  prefer_perpetuals: true          # Prefer perpetual swaps over dated
  allow_dated_contracts: true      # Allow quarterly/monthly contracts

correlation:
  enabled: true
  reference_asset: "BTCUSDT"
  
  # Calculation parameters
  timeframe: "5m"                  # 5-minute candles
  lookback_period_hours: 24        # Last 24 hours (rolling window)
  lookback_period_candles: 288     # 24h = 288 × 5m candles
  method: "pearson"                # Pearson correlation coefficient
  
  # Application rules
  max_corr: 0.2                    # Asset passes if |ρ| ≤ 0.2
  correlation_recheck: true        # Recheck periodically
  recalc_interval_minutes: 5       # Recalculate every 5 minutes
  
  # Monitoring during position
  emergency_corr: 0.5              # Emergency exit if |ρ| > 0.5
  emergency_check_interval_minutes: 5
  warning_corr: 0.35               # Log warning if |ρ| > 0.35
  
  # Special cases
  allow_corr_waivers: false        # Don't allow exceptions to correlation filter
  correlation_persistence: true    # Remember recent correlations

manipulation:
  enabled: true
  lookback_days: 3                 # Last 3 days analysis
  lookback_bars_m15: 288           # 3 days × 288 bars
  timeframes: ["15m", "1h"]        # Check M15 and H1
  
  # Anomaly detection parameters
  anomaly_k1: 3.0                  # Wick multiplier (k1 × avg body)
  anomaly_k2: 2.0                  # ATR multiplier (k2 × ATR(14))
  anomaly_k3: 3.0                  # Volume multiplier (k3 × avg vol)
  
  # Thresholds
  threshold_anomalies: 5           # Mark as manipulation if ≥ 5 anomalies
  ban_duration_hours: 72           # 3-day ban for manipulation
  
  # Exception trading
  exception_limit_pct: 10          # Allow up to 10% of daily trades
  require_perfect_setup: true      # Only FVG_TREND_COMBO allowed for exceptions
  exception_boost_confidence: true # Boost confidence for exceptions

technical:
  min_atr_percent: 0.1             # Min 0.1% ATR (too flat)
  max_atr_percent: 5.0             # Max 5% ATR (too volatile)
  min_volume_ma: 1000              # Min volume (MA)

tagging:
  enable_tags: true
  tags:
    - "trending"                   # Strong uptrend
    - "consolidating"              # Ranging market
    - "volatile"                   # High volatility
    - "illiquid"                   # Low volume
    - "hot_topic"                  # Viral/pumping
    - "micro_cap"                  # Small market cap

scanning:
  batch_size: 50                   # Process 50 assets per batch
  skip_already_held: true          # Don't scan assets with open positions
```

---

## config/schedule.yaml (Complete)

```yaml
################################
# Operating Hours & News Windows
# Controls when bot can open new positions
################################

liquidity:
  always_open: true                # Default: trade 24/7 with exceptions
  
  # Low-liquidity windows (NO NEW SIGNALS)
  low_liquidity_hours:
    enabled: true
    start_hour: 3
    end_hour: 7
    timezone: "UTC"
    day_of_week: 5                 # Friday (0=Monday, 5=Friday)
    reason: "Asian market close, low liquidity"
  
  # Position management continues during low liquidity
  allow_exits_during_low_liquidity: true
  allow_emergency_closes: true

news_windows:
  enabled: true
  check_economic_calendar: false   # Requires news API
  
  # Major economic events (NO NEW SIGNALS)
  events:
    - name: "FOMC"
      abbrev: "FOMC"
      before_minutes: 60
      after_minutes: 60
      importance: "critical"       # critical, high, medium, low
      country: "US"
      
    - name: "CPI"
      abbrev: "CPI"
      before_minutes: 30
      after_minutes: 30
      importance: "high"
      country: "US"
      
    - name: "NFP (Non-Farm Payroll)"
      abbrev: "NFP"
      before_minutes: 60
      after_minutes: 60
      importance: "critical"
      country: "US"
      
    - name: "PMI Manufacturing"
      abbrev: "PMI"
      before_minutes: 30
      after_minutes: 30
      importance: "high"
      country: "US"
      
    - name: "ECB"
      abbrev: "ECB"
      before_minutes: 60
      after_minutes: 60
      importance: "critical"
      country: "EU"
      
    - name: "BOE"
      abbrev: "BOE"
      before_minutes: 60
      after_minutes: 60
      importance: "critical"
      country: "UK"

maintenance:
  # Auto-stop times (UTC)
  maintenance_windows:
    - day: "Monday"
      start_time: "00:00"
      end_time: "01:00"
      reason: "Weekly maintenance"
    
    - day: "Friday"
      start_time: "23:00"
      end_time: "24:00"
      reason: "Weekend preparation"

alerts:
  enable_alerts: true
  alert_types:
    - "signal_generated"           # New signal created
    - "position_opened"            # Position filled
    - "position_closed"            # Position exited
    - "emergency_exit"             # Emergency close triggered
    - "correlation_spike"          # Correlation spike detected
    - "manipulation_detected"      # Pump-dump detected
    - "error"                      # Error occurred
    - "daily_summary"              # End-of-day summary

performance_tracking:
  daily_report_time: "23:55"       # Generate report at 23:55 UTC
  weekly_report_day: 5             # Friday
  monthly_report_day: 1            # 1st of month

backup:
  enabled: true
  backup_interval_hours: 6
  backup_directory: "data/backups"
  keep_backups_days: 30
```

---

## .env.example (Complete)

```bash
################################
# Environment Variables
# Copy to .env and fill with your values
################################

# === OKX API Credentials (REQUIRED) ===
OKX_API_KEY=your_api_key_here
OKX_API_SECRET=your_api_secret_here
OKX_PASSPHRASE=your_passphrase_here

# === Bot Configuration ===
BOT_MODE=signal_only             # signal_only or live_trade
BOT_NAME=OKX-Short-Bot-01
BOT_VERSION=1.0.0

# === Database ===
DB_TYPE=sqlite
DB_PATH=data/trades.db

# === Logging ===
LOG_LEVEL=INFO                   # DEBUG, INFO, WARNING, ERROR
LOG_FILE=logs/app.log
LOG_FORMAT=default               # default or json

# === Operating Mode ===
SANDBOX_MODE=false               # true for OKX sandbox testing
PAPER_TRADING=false              # true for simulated mode

# === Proxy (Optional) ===
USE_PROXY=false
PROXY_URL=http://proxy:port

# === Email Alerts (Optional) ===
ENABLE_EMAIL_ALERTS=false
EMAIL_FROM=bot@example.com
EMAIL_TO=you@example.com
EMAIL_SMTP=smtp.gmail.com
EMAIL_SMTP_PORT=587
EMAIL_PASSWORD=your_app_password

# === Telegram Alerts (Optional) ===
ENABLE_TELEGRAM=false
TELEGRAM_BOT_TOKEN=your_token_here
TELEGRAM_CHAT_ID=your_chat_id

# === Performance Tuning ===
MAX_API_CALLS_PER_SECOND=10
CACHE_TIMEOUT_SECONDS=300
REQUEST_TIMEOUT_SECONDS=30

# === Strategy Parameters (Optional) ===
# Override config/risk.yaml values
LEVERAGE_OVERRIDE=10
MAX_RISK_PCT_OVERRIDE=5.0
MIN_RR_OVERRIDE=4.0

# === Debug Mode ===
DEBUG=false
VERBOSE=false
DRY_RUN=false

# === Backup & Data ===
AUTO_BACKUP=true
BACKUP_INTERVAL_HOURS=6
KEEP_HISTORICAL_DAYS=90
```

---

## pyproject.toml (Complete)

```toml
[build-system]
requires = ["setuptools>=65.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "okx-short-bot"
version = "1.0.0"
description = "Automated intraday short trading bot for OKX USDT futures"
readme = "README.md"
requires-python = ">=3.10"
license = {text = "MIT"}
authors = [
    {name = "OKX Bot Team", email = "bot@example.com"}
]
keywords = ["trading", "okx", "futures", "automated", "bot"]
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Financial and Insurance Industry",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Topic :: Office/Business :: Financial",
]

dependencies = [
    "okx>=1.5.0",
    "pandas>=1.5.0",
    "numpy>=1.24.0",
    "scipy>=1.9.0",
    "matplotlib>=3.6.0",
    "requests>=2.28.0",
    "python-dotenv>=0.20.0",
    "pyyaml>=6.0",
    "pylatexenc>=2.10",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.3.0",
    "pytest-cov>=4.1.0",
    "black>=23.3.0",
    "isort>=5.12.0",
    "flake8>=6.0.0",
    "mypy>=1.2.0",
]

[project.urls]
Homepage = "https://github.com/example/okx-short-bot"
Repository = "https://github.com/example/okx-short-bot.git"
Documentation = "https://github.com/example/okx-short-bot/wiki"
"Issue Tracker" = "https://github.com/example/okx-short-bot/issues"

[project.scripts]
okx-bot = "src.main:main"
okx-bot-backtest = "src.main:backtest"

[tool.setuptools]
packages = ["src"]

[tool.black]
line-length = 88
target-version = ['py310']
include = '\.pyi?$'

[tool.isort]
profile = "black"
line_length = 88
multi_line_mode = 3

[tool.mypy]
python_version = "3.10"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = false
disallow_any_generics = false

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
addopts = "-v --cov=src --cov-report=html"
```

---

**PART 8 Готова:**

✅ config/settings.yaml (полная) 
✅ config/risk.yaml (полная)
✅ config/filters.yaml (полная)
✅ config/schedule.yaml (полная)
✅ .env.example (полный)
✅ pyproject.toml (полный)

Все конфиги готовы к использованию! 🎯

Готов к PART 9 (примеры использования, скрипты, примеры вывода)?
