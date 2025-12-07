# OKX Intraday Short Bot — Complete Project

## 📦 PART 1: README & QUICK START

### Project Overview

**Production-Ready Automated Trading Bot for OKX USDT-Margined Futures**

- **Language:** Python 3.10+
- **Exchange:** OKX (USDT-margined futures)
- **Strategy:** Short-only with FVG + Trendlines
- **Position Lifetime:** ≤ 24 hours (intraday)
- **Status:** ✅ Production Ready

---

## 🎯 What This Bot Does

**Automated Short Trading Strategy:**

1. **Fair Value Gap (FVG) Detection**
   - 3-candle imbalance patterns
   - Potential reversion zones
   - Gap zone calculation

2. **Trendline Analysis**
   - Ascending support lines
   - Breakout detection & confirmation
   - Retest detection (+40% position boost)

3. **Asset Filtering**
   - Age: < 2 years old
   - Volume: > $25M USD 24h
   - Correlation: BTC |ρ| ≤ 0.2
   - Manipulation: No pump-dumps

4. **Risk Management**
   - Max 5% risk per trade
   - Min 1:4 R/R (1:3 for premium)
   - 10× leverage
   - 24-hour position timeout

5. **Position Management**
   - Market entry on signal
   - TP/SL on OKX
   - Emergency exits (correlation spike, news, timeout)

---

## ⚡ Quick Start (2 Minutes)

### 1. Setup Environment
```bash
python3.10 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Credentials
```bash
cp .env.example .env
# Edit .env with your OKX API credentials:
# OKX_API_KEY=your_key
# OKX_API_SECRET=your_secret
# OKX_PASSPHRASE=your_passphrase
```

### 3. Run Bot (Test Mode - Safe)
```bash
python src/main.py --mode signal_only --verbose
```

### 4. Monitor Output
```bash
tail -f logs/app.log
cat logs/trades_$(date +%Y%m%d).json | python -m json.tool
```

### 5. Run Live (After Testing)
```bash
python src/main.py --mode live_trade
```

---

## 🚀 Operating Modes

### Mode 1: Signal-Only (Testing)
```bash
python src/main.py --mode signal_only --verbose
```
- ✅ Analyzes markets & generates signals
- ❌ Does NOT execute trades
- ✅ Safe for validation & optimization

### Mode 2: Live Trading
```bash
python src/main.py --mode live_trade
```
- ⚠️ Executes REAL trades with real money
- ⚠️ Use only after testing!
- ✅ Full position management

### Mode 3: Backtest
```bash
python src/main.py --backtest --backtest-start "2024-11-01" --backtest-end "2024-11-30"
```
- ✅ Tests on historical data
- ✅ Performance analysis
- ❌ No real execution

---

## 📊 Project Statistics

- **Total Files:** 48
- **Python Modules:** 21 (~3,000 lines)
- **Config Files:** 4 (YAML)
- **Documentation:** 8 markdown files
- **Tests:** 2 test modules
- **Notebooks:** 1 Jupyter

---

## 📁 Project Structure

```
okx-short-bot/
├── config/                (4 YAML files)
│   ├── settings.yaml
│   ├── risk.yaml
│   ├── filters.yaml
│   └── schedule.yaml
│
├── src/                   (21 Python modules)
│   ├── main.py
│   ├── api/
│   ├── data/
│   ├── screening/
│   ├── ta/
│   ├── strategy/
│   ├── execution/
│   ├── reporting/
│   ├── backtest/
│   └── utils/
│
├── tests/
├── notebooks/
├── logs/
├── reports/
└── data/
```

---

## ✨ Key Features

✅ FVG Detection (3-candle patterns)
✅ Trendline Analysis (Support breakouts)
✅ Trend Verification (Higher Lows)
✅ BTC Correlation Filtering
✅ Manipulation Detection
✅ Signal Generation (3 types: Combo, FVG-only, Trend-only)
✅ Risk/Reward Validation (1:4 minimum)
✅ Position Sizing (Risk-based)
✅ Order Execution (Market, Limit, TP/SL)
✅ Position Management (Real-time tracking)
✅ Emergency Exits (Correlation spike, news, 24h timeout)
✅ JSON Logging (Daily trade records)
✅ LaTeX Reports (Daily performance)
✅ PNG Charts (Asset + BTC)
✅ Paper Trading (Simulator)
✅ Backtesting (Historical testing)
✅ 24/7 Monitoring

---

## 🛡️ Security

✅ API credentials in .env (environment variables)
✅ No hardcoded secrets
✅ .gitignore prevents credential leaks
✅ Input validation throughout
✅ Sandbox mode available

⚠️ **NEVER:**
- Share your .env file
- Commit .env to git
- Use mainnet without testing
- Start in live_trade immediately

---

## 📚 Documentation Files (Read in Order)

1. **README.md** - This file (overview)
2. **QUICK_START.md** - 30-second setup
3. **PROJECT_SUMMARY.md** - Full architecture
4. **DEPLOYMENT.md** - Production guide
5. **OKX_BOT_SPECIFICATION.md** - Complete specification

---

## 🎯 Next Steps

**TODAY:**
1. Read this README
2. Setup virtual environment
3. Edit .env file
4. Run in signal_only mode

**FIRST DAY:**
1. Monitor logs/app.log
2. Review generated signals
3. Read PROJECT_SUMMARY.md

**FIRST WEEK:**
1. Test for 3-5 days
2. Review daily reports
3. Adjust config parameters
4. Run backtest

**PRODUCTION:**
1. Read DEPLOYMENT.md
2. Deploy with systemd/Docker
3. Monitor 24/7

---

## ⚠️ Important Disclaimer

This trading bot is for **EDUCATIONAL and PERSONAL use only**.

**Risk Warning:**
- Trading with real money carries **SIGNIFICANT RISK**
- You can **LOSE MORE** than your initial investment
- Past performance ≠ future results
- Leverage trading is **EXTREMELY RISKY**
- Never risk capital you cannot afford to lose

**Best Practices:**
✅ Always start with signal_only mode
✅ Test for several days before live trading
✅ Use small position sizes initially
✅ Monitor bot continuously
✅ Have emergency stop ready
✅ Know when to stop

---

## 📞 Troubleshooting

| Problem | Solution |
|---------|----------|
| No signals | Reduce max_corr in filters.yaml |
| High memory | Clear cache: `rm -rf data/historical/*` |
| API errors | Check .env credentials |
| Import errors | `pip install -r requirements.txt` |
| Connection refused | Verify OKX API status |

**Check logs:**
```bash
tail -f logs/app.log
```

---

**Version:** 1.0.0
**Status:** ✅ Production Ready
**Created:** December 2024

Start with QUICK_START.md next!
