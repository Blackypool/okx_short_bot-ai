# OKX Intraday Short Bot — PART 2: CONFIGURATION FILES

## 📋 PART 2: Configuration Files

All YAML configuration files with full documentation.

---

## config/settings.yaml

```yaml
# OKX Short Bot - Main Settings
# Last Updated: December 2024

bot:
  name: "OKX Intraday Short Bot"
  version: "1.0.0"
  mode: "signal_only"              # Change to "live_trade" for real execution
  verbose: true
  log_level: "INFO"                # DEBUG, INFO, WARNING, ERROR

exchange:
  name: "OKX"
  api_key: "${OKX_API_KEY}"        # From .env file
  api_secret: "${OKX_API_SECRET}"  # From .env file
  passphrase: "${OKX_PASSPHRASE}"  # From .env file
  sandbox: false                   # Set true for testing
  rest_url: "https://www.okx.com"

timezone: "UTC"

database:
  type: "sqlite"
  path: "data/trades.db"

monitoring:
  enable_alerts: true
  alert_channels: ["log", "email"]
  email_recipient: "your_email@example.com"
```

---

## config/risk.yaml

```yaml
# Risk Management Settings
# Critical: These parameters control position sizing and risk

position:
  leverage: 10                     # 10× leverage on USDT-margined futures
  max_risk_pct: 5.0                # Max 5% of deposit at risk per trade
  min_rr: 4.0                      # Minimum 1:4 Risk/Reward ratio
  premium_rr: 3.0                  # 1:3 for perfect technical setups
  premium_setup_flags:             # Conditions for premium R/R
    - "perfect_retest"
    - "fvg_trend_combo"
    - "high_confluence"

position_sizing:
  method: "risk_based"             # risk_based or fixed_size
  fixed_size_usd: 100.0            # If using fixed sizing
  scale_with_volatility: true
  volatility_multiplier: 0.8       # Adjust size by volatility

takeprofit:
  mode: "single"                   # single or two_level
  two_level_split: 0.5             # 50% at first target, 50% at second

stoploss:
  buffer_atr_multiplier: 0.1       # Add 10% of ATR(14) for wick protection
  buffer_pct: 0.5                  # Or 0.5% absolute buffer
  use_atr: true                    # Prefer ATR-based buffer

max_positions:
  total: 5                         # Max 5 open positions
  per_asset: 1                     # Max 1 position per asset

daily_limits:
  max_trades: 20                   # Max trades per day
  max_loss_pct: 10.0               # Stop trading if day loss > 10%
  max_loss_usd: 5000.0             # Or if loss > $5000

timeout:
  position_lifetime_hours: 24      # Close positions after 24 hours

emergency:
  correlation_spike_threshold: 0.5 # Close if |ρ| > 0.5
  news_event_stop: true
  max_consecutive_losses: 3        # Close all positions after 3 losses in row
```

---

## config/filters.yaml

```yaml
# Asset Screening & Filtering Rules
# Determines which contracts are eligible for trading

universe:
  # Age filter
  min_age_days: 0
  max_age_days: 730               # Max 2 years old

  # Volume filter
  min_volume_usd: 25000000        # Min $25M 24h volume

  # Status filter
  exclude_delisting: true
  exclude_settlement: true
  exclude_suspended: true

correlation:
  enabled: true
  reference_asset: "BTCUSDT"
  
  # Calculation
  timeframe: "5m"                 # 5-minute candles
  lookback_period_hours: 24       # Last 24 hours
  method: "pearson"               # Pearson correlation coefficient
  
  # Application
  max_corr: 0.2                   # Asset passes if |ρ| ≤ 0.2
  recalc_interval_minutes: 5      # Recalculate every 5 min
  
  # Monitoring
  emergency_corr: 0.5             # Emergency exit if |ρ| > 0.5
  warning_corr: 0.35              # Log warning if |ρ| > 0.35

manipulation:
  enabled: true
  lookback_days: 3
  timeframes: ["15m", "1h"]
  
  # Anomaly detection parameters
  anomaly_k1: 3.0                 # Wick multiplier (k1 × avg body)
  anomaly_k2: 2.0                 # ATR multiplier (k2 × ATR(14))
  anomaly_k3: 3.0                 # Volume multiplier (k3 × avg vol)
  
  # Thresholds
  threshold_anomalies: 5          # Mark as manipulation if ≥ 5 anomalies
  ban_duration_hours: 72          # 3-day ban
  
  # Exception trading
  exception_limit_pct: 10         # Allow up to 10% of daily trades
  require_perfect_setup: true     # Only FVG_TREND_COMBO allowed

tagging:
  enable_tags: true
  tags:
    - "trending"
    - "consolidating"
    - "volatile"
    - "illiquid"
```

---

## config/schedule.yaml

```yaml
# Operating Hours & News Windows
# Defines when bot can open new positions

liquidity:
  always_open: true              # Default: trade 24/7
  
  # Low-liquidity windows (NO NEW SIGNALS)
  low_liquidity_hours:
    start_hour: 3
    end_hour: 7
    timezone: "UTC"              # Friday 3-7 UTC (avoid low liquidity)
  
  # Position management continues during low liquidity

news_windows:
  enabled: true
  
  # Major economic events (NO NEW SIGNALS)
  events:
    - name: "FOMC"
      before_minutes: 60
      after_minutes: 60
      importance: "critical"
    
    - name: "CPI"
      before_minutes: 30
      after_minutes: 30
      importance: "high"
    
    - name: "NFP"
      before_minutes: 60
      after_minutes: 60
      importance: "critical"
    
    - name: "PMI"
      before_minutes: 30
      after_minutes: 30
      importance: "high"

maintenance:
  # Auto-stop times (UTC)
  maintenance_windows:
    - day: "Monday"
      start_time: "00:00"
      end_time: "01:00"
    
    - day: "Friday"
      start_time: "23:00"
      end_time: "24:00"

alerts:
  enable_alerts: true
  alert_types:
    - "signal_generated"
    - "position_opened"
    - "position_closed"
    - "emergency_exit"
    - "correlation_spike"
    - "error"
```

---

## .env.example

```bash
# OKX API Credentials
# Copy this file to .env and fill with your credentials

# OKX API Key
OKX_API_KEY=your_api_key_here

# OKX API Secret
OKX_API_SECRET=your_api_secret_here

# OKX Passphrase (for SPOT trading permissions)
OKX_PASSPHRASE=your_passphrase_here

# Operating Mode
BOT_MODE=signal_only             # signal_only or live_trade

# Database
DB_PATH=data/trades.db

# Logging
LOG_LEVEL=INFO                   # DEBUG, INFO, WARNING, ERROR
LOG_FILE=logs/app.log

# Email Alerts (optional)
ENABLE_EMAIL_ALERTS=false
EMAIL_FROM=bot@example.com
EMAIL_TO=you@example.com
EMAIL_PASSWORD=your_email_password

# Proxy (optional, for access from restricted regions)
USE_PROXY=false
PROXY_URL=http://proxy:port

# Testing
SANDBOX_MODE=false               # Set true to use OKX sandbox
```

---

## requirements.txt

```
# OKX Short Bot Dependencies
# Install with: pip install -r requirements.txt

# Exchange APIs
ccxt==3.1.1
okx>=1.5.0

# Data Science
pandas>=1.5.0
numpy>=1.24.0
scipy>=1.9.0

# Charts & Visualization
matplotlib>=3.6.0
seaborn>=0.12.0

# HTTP & Configuration
requests>=2.28.0
pyyaml>=6.0
python-dotenv>=0.20.0

# Utilities
python-dateutil>=2.8.2
pytz>=2023.3

# Logging
python-json-logger>=2.0.7

# LaTeX Report Generation
pylatexenc>=2.10

# Testing (optional)
pytest>=7.3.0
pytest-cov>=4.1.0

# Development (optional)
black>=23.3.0
isort>=5.12.0
flake8>=6.0.0
mypy>=1.2.0
