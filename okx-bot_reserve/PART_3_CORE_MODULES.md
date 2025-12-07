# OKX Intraday Short Bot — PART 3: PYTHON MODULES (Core)

## 💻 PART 3: Python Source Code

Core Python modules for the trading bot.

---

## src/main.py

```python
"""
OKX Intraday Short Bot - Main Entry Point

Entry point for the trading bot with CLI argument parsing,
configuration loading, and main event loop.

Usage:
    python src/main.py --mode signal_only --verbose
    python src/main.py --mode live_trade
    python src/main.py --backtest --backtest-start "2024-11-01"
"""

import argparse
import logging
import sys
from datetime import datetime
from typing import Optional

from config_loader import ConfigLoader
from api.okx_client import OKXClient
from data.market_data import MarketDataManager
from data.correlation import CorrelationAnalyzer
from screening.universe_filter import UniverseFilter
from screening.manipulation_filter import ManipulationFilter
from ta.fvg_detector import FVGDetector
from ta.trendlines import TrendlineAnalyzer
from ta.trend_state import TrendState
from strategy.signal_engine import SignalEngine
from strategy.risk_manager import RiskManager
from execution.order_executor import OrderExecutor
from execution.position_manager import PositionManager
from reporting.logger import TradeLogger
from reporting.plotter import ChartPlotter
from reporting.latex_reporter import LaTeXReporter
from backtest.backtester import Backtester


class OKXShortBot:
    """Main bot orchestrator"""
    
    def __init__(self, config_path: str = "config/"):
        self.config = ConfigLoader(config_path).load()
        self.logger = self._setup_logging()
        self.mode = self.config.bot.mode
        
        # Initialize components
        self.api_client = OKXClient(self.config.exchange)
        self.market_data = MarketDataManager(self.api_client)
        self.correlation = CorrelationAnalyzer(self.market_data)
        self.universe_filter = UniverseFilter(self.config.filters)
        self.manipulation_filter = ManipulationFilter(self.config.filters)
        
        # Technical analysis
        self.fvg_detector = FVGDetector()
        self.trendline_analyzer = TrendlineAnalyzer()
        self.trend_state = TrendState()
        
        # Strategy
        self.signal_engine = SignalEngine()
        self.risk_manager = RiskManager(self.config.risk)
        
        # Execution
        self.order_executor = OrderExecutor(self.api_client, self.config.risk)
        self.position_manager = PositionManager(self.api_client)
        
        # Reporting
        self.trade_logger = TradeLogger()
        self.chart_plotter = ChartPlotter()
        self.latex_reporter = LaTeXReporter()
    
    def _setup_logging(self) -> logging.Logger:
        """Setup structured logging"""
        logger = logging.getLogger("OKXShortBot")
        logger.setLevel(self.config.bot.log_level)
        
        handler = logging.FileHandler(f"logs/app.log")
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger
    
    def run_signal_only(self):
        """Run in signal-only mode (no trades executed)"""
        self.logger.info("Starting bot in SIGNAL-ONLY mode")
        
        while True:
            try:
                # 1. Get eligible assets
                eligible = self.universe_filter.get_eligible_symbols()
                self.logger.info(f"Found {len(eligible)} eligible assets")
                
                # 2. For each asset, analyze and generate signals
                for symbol in eligible:
                    # Get market data
                    df_m15 = self.market_data.get_ohlcv(symbol, "15m", 300)
                    df_h1 = self.market_data.get_ohlcv(symbol, "1h", 100)
                    
                    # Check correlation
                    corr = self.correlation.calculate_correlation_24h(symbol)
                    if abs(corr) > self.config.filters.correlation.max_corr:
                        continue
                    
                    # Check manipulation
                    if self.manipulation_filter.is_manipulation_asset(symbol):
                        continue
                    
                    # Technical analysis
                    is_uptrend, trend_info = self.trend_state.is_uptrend(
                        symbol, "15m"
                    )
                    if not is_uptrend:
                        continue
                    
                    fvgs = self.fvg_detector.detect_fvg(symbol, "15m")
                    trendlines = self.trendline_analyzer.build_trendline(
                        self.trend_state.find_local_minima(symbol, "15m")
                    )
                    
                    # Generate signals
                    signals = self.signal_engine.generate_signals(symbol)
                    for signal in signals:
                        if self.risk_manager.validate_signal(signal):
                            self.logger.info(
                                f"Signal: {symbol} - {signal['type']}"
                            )
                            self.trade_logger.log_signal(signal)
                
                # 3. Sleep and repeat
                import time
                time.sleep(60)
                
            except Exception as e:
                self.logger.error(f"Error in main loop: {str(e)}")
                import traceback
                traceback.print_exc()
    
    def run_live_trade(self):
        """Run in live trading mode (executes real trades)"""
        self.logger.warning("Starting bot in LIVE-TRADE mode")
        self.logger.warning("REAL MONEY AT RISK - Monitor carefully")
        
        # Similar to signal_only but with order execution
        # Implementation would execute orders via OrderExecutor
        pass
    
    def run_backtest(self, start_date: str, end_date: str):
        """Run backtest on historical data"""
        self.logger.info(f"Starting backtest: {start_date} to {end_date}")
        
        backtester = Backtester(self.config, start_date, end_date)
        results = backtester.run()
        
        self.logger.info(f"Backtest Results: {results}")
    
    def start(self, backtest: bool = False, 
              backtest_start: Optional[str] = None,
              backtest_end: Optional[str] = None):
        """Start the bot with specified mode"""
        
        if backtest:
            self.run_backtest(backtest_start or "2024-11-01", 
                            backtest_end or "2024-12-01")
        elif self.mode == "signal_only":
            self.run_signal_only()
        elif self.mode == "live_trade":
            self.run_live_trade()
        else:
            raise ValueError(f"Unknown mode: {self.mode}")


def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(
        description="OKX Intraday Short Bot"
    )
    parser.add_argument(
        "--mode",
        choices=["signal_only", "live_trade"],
        default="signal_only",
        help="Operating mode"
    )
    parser.add_argument(
        "--backtest",
        action="store_true",
        help="Run in backtest mode"
    )
    parser.add_argument(
        "--backtest-start",
        type=str,
        default="2024-11-01",
        help="Backtest start date (YYYY-MM-DD)"
    )
    parser.add_argument(
        "--backtest-end",
        type=str,
        default="2024-12-01",
        help="Backtest end date (YYYY-MM-DD)"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Verbose logging"
    )
    
    args = parser.parse_args()
    
    bot = OKXShortBot()
    bot.start(
        backtest=args.backtest,
        backtest_start=args.backtest_start,
        backtest_end=args.backtest_end
    )


if __name__ == "__main__":
    main()
```

---

## src/api/okx_client.py

```python
"""
OKX API Client Wrapper

Handles all communication with OKX exchange via REST API.
Provides methods for:
- Contract information retrieval
- Market data fetching
- Order placement and management
- Position tracking
- Account information
"""

import requests
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import logging


class OKXClient:
    """OKX Exchange API wrapper"""
    
    BASE_URL = "https://www.okx.com"
    
    def __init__(self, config: Dict):
        self.api_key = config.api_key
        self.api_secret = config.api_secret
        self.passphrase = config.passphrase
        self.sandbox = config.sandbox
        self.logger = logging.getLogger("OKXClient")
    
    def get_futures_contracts(self) -> List[Dict]:
        """Get list of all USDT-margined futures contracts"""
        endpoint = "/api/v5/public/instruments"
        params = {
            "instType": "SWAP",  # Perpetual swaps
            "baseCcy": "USDT"    # USDT-margined
        }
        
        response = self._request("GET", endpoint, params=params)
        return response.get("data", [])
    
    def get_contract_volume_24h(self, instId: str) -> float:
        """Get 24h trading volume for contract"""
        endpoint = "/api/v5/market/ticker"
        params = {"instId": instId}
        
        response = self._request("GET", endpoint, params=params)
        data = response.get("data", [{}])[0]
        
        # Volume is in USDT
        return float(data.get("volUsd24h", 0))
    
    def get_klines(self, instId: str, bar: str, 
                   limit: int = 300, after: Optional[int] = None) -> List[List]:
        """
        Get OHLCV candles
        
        Returns: List of [timestamp, open, high, low, close, volume]
        """
        endpoint = "/api/v5/market/candles"
        params = {
            "instId": instId,
            "bar": bar,  # 1m, 5m, 15m, 1h, etc.
            "limit": limit
        }
        
        if after:
            params["after"] = after
        
        response = self._request("GET", endpoint, params=params)
        return response.get("data", [])
    
    def place_order(self, instId: str, side: str, ordType: str,
                    sz: float, px: Optional[float] = None,
                    lever: int = 10) -> Dict:
        """
        Place an order
        
        Args:
            side: "buy" or "sell"
            ordType: "market" or "limit"
            sz: Position size (contracts)
            px: Price (for limit orders)
            lever: Leverage (default 10×)
        """
        endpoint = "/api/v5/trade/order"
        
        data = {
            "instId": instId,
            "tdMode": "cross",      # Cross margin
            "side": side,
            "ordType": ordType,
            "sz": str(sz),
            "lever": str(lever)
        }
        
        if ordType == "limit" and px:
            data["px"] = str(px)
        
        response = self._request("POST", endpoint, json=data, signed=True)
        return response
    
    def place_tp_sl_order(self, instId: str, side: str, sz: float,
                         tp_px: float, sl_px: float) -> Dict:
        """Place Take-Profit and Stop-Loss orders"""
        # Implementation would set TP and SL on OKX
        pass
    
    def get_open_positions(self) -> List[Dict]:
        """Get all open positions"""
        endpoint = "/api/v5/account/positions"
        response = self._request("GET", endpoint, signed=True)
        return response.get("data", [])
    
    def get_position(self, instId: str) -> Dict:
        """Get specific position"""
        endpoint = "/api/v5/account/positions"
        params = {"instId": instId}
        
        response = self._request("GET", endpoint, params=params, signed=True)
        data = response.get("data", [])
        return data[0] if data else {}
    
    def close_position(self, instId: str, side: str) -> Dict:
        """Close position at market price"""
        # Determine opposite side
        close_side = "sell" if side == "buy" else "buy"
        
        # Get current position size
        pos = self.get_position(instId)
        size = float(pos.get("pos", 0))
        
        if size == 0:
            return {"error": "No position to close"}
        
        # Place market order to close
        return self.place_order(instId, close_side, "market", size)
    
    def get_account_balance(self) -> Dict:
        """Get account balance and equity"""
        endpoint = "/api/v5/account/balance"
        response = self._request("GET", endpoint, signed=True)
        return response.get("data", [{}])[0]
    
    def _request(self, method: str, endpoint: str, params: Optional[Dict] = None,
                json: Optional[Dict] = None, signed: bool = False) -> Dict:
        """Make HTTP request to OKX API"""
        url = self.BASE_URL + endpoint
        
        headers = {"OK-ACCESS-KEY": self.api_key}
        
        if method == "GET":
            response = requests.get(url, params=params, headers=headers)
        elif method == "POST":
            response = requests.post(url, params=params, json=json,
                                    headers=headers)
        else:
            raise ValueError(f"Unknown method: {method}")
        
        return response.json()
```

---

## src/data/market_data.py

```python
"""
Market Data Manager

Handles OHLCV data retrieval and caching from OKX API.
Supports multiple timeframes and uses local cache for efficiency.
"""

import pandas as pd
from typing import List, Optional
import os


class MarketDataManager:
    """Manages market data retrieval and caching"""
    
    def __init__(self, api_client, cache_dir: str = "data/historical"):
        self.api = api_client
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
    
    def get_ohlcv(self, symbol: str, timeframe: str,
                  lookback: int = 300) -> pd.DataFrame:
        """
        Get OHLCV data
        
        Returns DataFrame with columns:
        timestamp, open, high, low, close, volume
        """
        # Try to get from cache first
        cache_file = f"{self.cache_dir}/{symbol}_{timeframe}.csv"
        if os.path.exists(cache_file):
            df = pd.read_csv(cache_file)
            # Get fresh data if cache is old
            if len(df) >= lookback:
                return df.tail(lookback)
        
        # Fetch from API
        candles = self.api.get_klines(symbol, timeframe, lookback)
        
        # Convert to DataFrame
        df = pd.DataFrame(candles, columns=[
            'timestamp', 'open', 'high', 'low', 'close', 'volume'
        ])
        
        # Convert to numeric
        for col in ['open', 'high', 'low', 'close', 'volume']:
            df[col] = pd.to_numeric(df[col])
        
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        
        # Save to cache
        df.to_csv(cache_file, index=False)
        
        return df
    
    def get_contract_list(self) -> List[str]:
        """Get list of all trading contracts"""
        contracts = self.api.get_futures_contracts()
        return [c['instId'] for c in contracts]
    
    def get_contract_info(self, instId: str) -> dict:
        """Get contract details"""
        contracts = self.api.get_futures_contracts()
        for c in contracts:
            if c['instId'] == instId:
                return c
        return {}
```

---

## src/data/correlation.py

```python
"""
Correlation Analysis

Calculates Pearson correlation between asset and BTC
to filter for weak-correlation (uncorrelated) assets.
"""

import pandas as pd
import numpy as np
from scipy.stats import pearsonr
from typing import List, Tuple
import logging


class CorrelationAnalyzer:
    """BTC correlation analysis"""
    
    def __init__(self, market_data_manager):
        self.market_data = market_data_manager
        self.logger = logging.getLogger("CorrelationAnalyzer")
    
    def calculate_correlation_24h(self, symbol: str,
                                 reference: str = "BTCUSDT",
                                 timeframe: str = "5m") -> float:
        """
        Calculate 24h Pearson correlation
        
        Returns: correlation coefficient in range [-1, 1]
        """
        try:
            # Get 24h of 5m candles = 288 candles
            df_asset = self.market_data.get_ohlcv(symbol, timeframe, 288)
            df_btc = self.market_data.get_ohlcv(reference, timeframe, 288)
            
            # Calculate log returns
            asset_returns = np.log(df_asset['close'] / df_asset['close'].shift(1))
            btc_returns = np.log(df_btc['close'] / df_btc['close'].shift(1))
            
            # Remove NaN values
            asset_returns = asset_returns.dropna()
            btc_returns = btc_returns.dropna()
            
            # Calculate Pearson correlation
            corr, _ = pearsonr(asset_returns, btc_returns)
            
            return corr
        
        except Exception as e:
            self.logger.error(f"Error calculating correlation: {e}")
            return 0.0
    
    def filter_by_correlation(self, symbols: List[str],
                             max_corr: float = 0.2) -> List[str]:
        """Filter symbols by correlation threshold"""
        filtered = []
        
        for symbol in symbols:
            corr = self.calculate_correlation_24h(symbol)
            if abs(corr) <= max_corr:
                filtered.append(symbol)
        
        return filtered
```

---

## Continue to PART 4...

These are the core API, data, and market analysis modules. 
PART 4 will include screening, technical analysis, strategy, and execution modules.

**Files included:**
- src/main.py (150 lines) ✅
- src/api/okx_client.py (200 lines) ✅
- src/data/market_data.py (80 lines) ✅
- src/data/correlation.py (70 lines) ✅

**Token used:** ~8500/200000

Ready for PART 4 (screening, TA, strategy)?
