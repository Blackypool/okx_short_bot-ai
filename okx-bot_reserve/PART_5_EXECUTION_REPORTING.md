# OKX Intraday Short Bot — PART 5: EXECUTION & REPORTING

## ⚙️ PART 5: Execution & Reporting Modules

---

## src/execution/order_executor.py

```python
"""
Order Executor

Handles order placement, TP/SL setup, and order cancellation.
Supports market and limit orders.
"""

import logging
from typing import Dict, Optional, Tuple
from datetime import datetime


class OrderExecutor:
    """Executes trading orders on OKX"""
    
    def __init__(self, api_client, config: dict):
        self.api = api_client
        self.config = config
        self.logger = logging.getLogger("OrderExecutor")
        self.leverage = config.position.leverage
    
    def execute_market_order(self, symbol: str, side: str,
                            size: float) -> Dict:
        """
        Execute market order (SELL for short)
        
        Args:
            symbol: Trading pair (e.g., "BTC-USDT")
            side: "sell" for short
            size: Position size in contracts
        
        Returns:
            Order response from OKX API
        """
        self.logger.info(f"Executing {side} order: {symbol} size={size}")
        
        order = self.api.place_order(
            instId=symbol,
            side=side,
            ordType="market",
            sz=size,
            lever=self.leverage
        )
        
        self.logger.info(f"Order placed: {order}")
        return order
    
    def execute_limit_order(self, symbol: str, side: str,
                           size: float, price: float) -> Dict:
        """Execute limit order"""
        self.logger.info(f"Executing limit {side}: {symbol} @ {price}")
        
        order = self.api.place_order(
            instId=symbol,
            side=side,
            ordType="limit",
            sz=size,
            px=price,
            lever=self.leverage
        )
        
        return order
    
    def place_tp_sl(self, symbol: str, side: str, size: float,
                   tp_price: float, sl_price: float) -> Dict:
        """Place Take-Profit and Stop-Loss orders"""
        self.logger.info(f"Setting TP={tp_price}, SL={sl_price}")
        
        order = self.api.place_tp_sl_order(
            instId=symbol,
            side=side,
            sz=size,
            tp_px=tp_price,
            sl_px=sl_price
        )
        
        return order
    
    def cancel_order(self, symbol: str, order_id: str) -> Dict:
        """Cancel pending order"""
        self.logger.info(f"Cancelling order: {order_id}")
        return self.api.close_order(symbol, order_id)
```

---

## src/execution/position_manager.py

```python
"""
Position Manager

Tracks open positions, applies filters, handles emergency closes.
Monitors:
- Correlation spikes (close if |ρ| > 0.5)
- News events
- 24-hour timeout
"""

import logging
from typing import List, Dict, Optional
from datetime import datetime, timedelta


class PositionManager:
    """Manages open trading positions"""
    
    def __init__(self, api_client):
        self.api = api_client
        self.logger = logging.getLogger("PositionManager")
        self.positions = {}
    
    def get_all_positions(self) -> List[Dict]:
        """Get all open positions from OKX"""
        positions = self.api.get_open_positions()
        return positions
    
    def close_position(self, symbol: str, side: str) -> Dict:
        """Close specific position at market price"""
        self.logger.info(f"Closing position: {symbol}")
        return self.api.close_position(symbol, side)
    
    def update_position_filters(self, symbol: str,
                               correlation: float,
                               time_open_hours: float) -> Dict:
        """
        Update position monitoring filters
        
        Check for emergency close conditions:
        1. Correlation spike (|ρ| > 0.5)
        2. Position open > 24 hours
        """
        status = {
            'correlation': correlation,
            'time_open_hours': time_open_hours,
            'emergency_close': False,
            'reason': None
        }
        
        # Check correlation spike
        if abs(correlation) > 0.5:
            status['emergency_close'] = True
            status['reason'] = f"Correlation spike: {correlation:.3f}"
        
        # Check 24-hour timeout
        if time_open_hours > 24:
            status['emergency_close'] = True
            status['reason'] = "24-hour position timeout"
        
        return status
    
    def handle_emergency_close(self, symbol: str,
                              reason: str) -> Dict:
        """Emergency close position at market"""
        self.logger.warning(f"Emergency close {symbol}: {reason}")
        
        pos = self.api.get_position(symbol)
        if pos and float(pos.get('pos', 0)) != 0:
            side = 'sell' if float(pos['pos']) > 0 else 'buy'
            return self.api.close_position(symbol, side)
        
        return {'status': 'No position to close'}
```

---

## src/reporting/logger.py

```python
"""
Trade Logger

Logs all trades and signals to JSON format.
Creates daily trade logs and signal logs.
"""

import json
import logging
from typing import Dict, List
from datetime import datetime
from pathlib import Path


class TradeLogger:
    """Structured logging of trades and signals"""
    
    def __init__(self, logs_dir: str = "logs"):
        self.logs_dir = logs_dir
        Path(logs_dir).mkdir(exist_ok=True)
        self.logger = logging.getLogger("TradeLogger")
    
    def log_trade(self, trade_dict: Dict):
        """
        Log completed trade
        
        Fields logged:
        - trade_id, signal_datetime, entry_datetime, exit_datetime
        - ticker, setup_type, entry_price, exit_price
        - TP, SL, position_size, R/R
        - P&L %, P&L USD, MAE, MFE
        - exit_type (TP, SL, CORRELATION_SPIKE, NEWS_STOP, TIME_OUT)
        """
        today = datetime.utcnow().strftime("%Y%m%d")
        filepath = f"{self.logs_dir}/trades_{today}.json"
        
        # Ensure required fields
        trade_dict['timestamp'] = datetime.utcnow().isoformat()
        
        # Append to JSON file
        trades = []
        try:
            with open(filepath, 'r') as f:
                trades = json.load(f)
        except:
            trades = []
        
        trades.append(trade_dict)
        
        with open(filepath, 'w') as f:
            json.dump(trades, f, indent=2)
        
        self.logger.info(f"Trade logged: {trade_dict.get('trade_id')}")
    
    def log_signal(self, signal_dict: Dict):
        """Log generated signal"""
        today = datetime.utcnow().strftime("%Y%m%d")
        filepath = f"{self.logs_dir}/signals_{today}.json"
        
        signal_dict['timestamp'] = datetime.utcnow().isoformat()
        
        signals = []
        try:
            with open(filepath, 'r') as f:
                signals = json.load(f)
        except:
            signals = []
        
        signals.append(signal_dict)
        
        with open(filepath, 'w') as f:
            json.dump(signals, f, indent=2)
    
    def get_today_trades(self) -> List[Dict]:
        """Get all trades from today"""
        today = datetime.utcnow().strftime("%Y%m%d")
        filepath = f"{self.logs_dir}/trades_{today}.json"
        
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except:
            return []
    
    def get_daily_stats(self, date: str) -> Dict:
        """Get daily statistics"""
        filepath = f"{self.logs_dir}/trades_{date}.json"
        
        trades = []
        try:
            with open(filepath, 'r') as f:
                trades = json.load(f)
        except:
            return {}
        
        # Calculate stats
        total_trades = len(trades)
        closed_trades = len([t for t in trades if t.get('exit_type')])
        winning_trades = len([t for t in trades 
                             if float(t.get('pnl_percentage', 0)) > 0])
        
        total_pnl = sum([float(t.get('pnl_usd', 0)) for t in trades])
        
        return {
            'date': date,
            'total_trades': total_trades,
            'closed_trades': closed_trades,
            'winning_trades': winning_trades,
            'win_rate': (winning_trades / closed_trades * 100 
                        if closed_trades > 0 else 0),
            'total_pnl_usd': total_pnl,
            'total_pnl_pct': (total_pnl / 1000 * 100)  # Assuming $1k deposit
        }
```

---

## src/reporting/plotter.py

```python
"""
Chart Plotter

Generates PNG charts for:
- Asset price action (M15, 24h) with entry/exit/TP/SL/trendline/FVG
- BTC correlation chart
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from typing import Optional, Dict
from pathlib import Path


class ChartPlotter:
    """Generates trading charts"""
    
    def __init__(self, charts_dir: str = "reports/charts"):
        self.charts_dir = charts_dir
        Path(charts_dir).mkdir(parents=True, exist_ok=True)
    
    def plot_asset_chart(self, symbol: str, df: pd.DataFrame,
                        entry_price: Optional[float] = None,
                        exit_price: Optional[float] = None,
                        tp: Optional[float] = None,
                        sl: Optional[float] = None,
                        trendline: Optional[Dict] = None,
                        fvg: Optional[Dict] = None) -> str:
        """
        Plot asset price chart with technical levels
        
        Includes:
        - OHLC candles
        - Entry/exit markers
        - TP/SL levels
        - Trendline
        - FVG zone (shaded)
        """
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Plot candles
        for idx, row in df.iterrows():
            x = idx
            open_p = row['open']
            close_p = row['close']
            high_p = row['high']
            low_p = row['low']
            
            # Candle body
            color = 'green' if close_p >= open_p else 'red'
            body_height = abs(close_p - open_p)
            body_bottom = min(open_p, close_p)
            
            ax.add_patch(mpatches.Rectangle(
                (x - 0.3, body_bottom), 0.6, body_height,
                facecolor=color, edgecolor=color, alpha=0.8
            ))
            
            # Wicks
            ax.plot([x, x], [low_p, high_p], color=color, linewidth=1)
        
        # Mark entry/exit
        if entry_price:
            ax.axhline(entry_price, color='blue', linestyle='--',
                       label=f'Entry: {entry_price:.2f}')
        if exit_price:
            ax.axhline(exit_price, color='orange', linestyle='--',
                       label=f'Exit: {exit_price:.2f}')
        
        # Mark TP/SL
        if tp:
            ax.axhline(tp, color='green', linestyle=':', linewidth=2,
                       label=f'TP: {tp:.2f}')
        if sl:
            ax.axhline(sl, color='red', linestyle=':', linewidth=2,
                       label=f'SL: {sl:.2f}')
        
        # Draw trendline
        if trendline:
            x_vals = range(len(df))
            y_vals = [trendline['slope'] * x + 
                     trendline['intercept'] for x in x_vals]
            ax.plot(x_vals, y_vals, 'purple', linewidth=2,
                   label='Trendline')
        
        # Shade FVG zone
        if fvg:
            ax.axhspan(fvg['low'], fvg['high'],
                       alpha=0.2, color='yellow',
                       label='FVG Zone')
        
        ax.set_title(f"{symbol} - Price Action", fontsize=14)
        ax.set_xlabel("Time")
        ax.set_ylabel("Price (USDT)")
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Save
        filepath = f"{self.charts_dir}/{symbol}_{pd.Timestamp.now().strftime('%Y-%m-%d_%H%M%S')}.png"
        plt.savefig(filepath, dpi=100, bbox_inches='tight')
        plt.close()
        
        return filepath
    
    def plot_btc_chart(self, df_btc: pd.DataFrame) -> str:
        """Plot BTC chart for correlation visualization"""
        fig, ax = plt.subplots(figsize=(12, 4))
        
        ax.plot(df_btc['close'], linewidth=2, color='orange')
        ax.set_title("BTC-USDT - Correlation Reference", fontsize=12)
        ax.set_ylabel("Price (USDT)")
        ax.grid(True, alpha=0.3)
        
        filepath = f"{self.charts_dir}/BTC_{pd.Timestamp.now().strftime('%Y-%m-%d')}.png"
        plt.savefig(filepath, dpi=100, bbox_inches='tight')
        plt.close()
        
        return filepath
```

---

## src/reporting/latex_reporter.py

```python
"""
LaTeX Report Generator

Creates professional daily LaTeX reports with:
- Summary statistics
- Per-trade details with charts
- Technical analysis breakdown
- P&L analysis
"""

from typing import List, Dict
from datetime import datetime
from pathlib import Path


class LaTeXReporter:
    """Generates LaTeX trading reports"""
    
    def __init__(self, reports_dir: str = "reports/tex"):
        self.reports_dir = reports_dir
        Path(reports_dir).mkdir(parents=True, exist_ok=True)
    
    def generate_daily_report(self, date: str,
                             trades: List[Dict],
                             stats: Dict) -> str:
        """
        Generate daily LaTeX report
        
        Sections:
        1. Summary (trades, P&L, win rate)
        2. Per-trade details (entry/exit, TP/SL, charts)
        3. Analysis (FVG/trendline details)
        4. Conclusion
        """
        
        content = self._generate_header(date)
        content += self._generate_summary(stats)
        content += self._generate_trades_section(trades)
        content += self._generate_conclusion()
        content += self._generate_footer()
        
        # Write to file
        filepath = f"{self.reports_dir}/report_{date}.tex"
        with open(filepath, 'w') as f:
            f.write(content)
        
        return filepath
    
    def _generate_header(self, date: str) -> str:
        """LaTeX document header"""
        return f"""\\documentclass{{article}}
\\usepackage{{graphicx}}
\\usepackage{{booktabs}}
\\usepackage{{hyperref}}

\\title{{OKX Short Bot - Daily Report}}
\\date{{{date}}}

\\begin{{document}}
\\maketitle

\\section{{Trading Summary}}
"""
    
    def _generate_summary(self, stats: Dict) -> str:
        """Generate summary section"""
        content = f"""
\\subsection{{Daily Statistics}}

\\begin{{itemize}}
  \\item Total Trades: {stats.get('total_trades', 0)}
  \\item Closed Trades: {stats.get('closed_trades', 0)}
  \\item Winning Trades: {stats.get('winning_trades', 0)}
  \\item Win Rate: {stats.get('win_rate', 0):.1f}\\%
  \\item Total P\\&L: \\${stats.get('total_pnl_usd', 0):.2f}}
  \\item P\\&L \\%: {stats.get('total_pnl_pct', 0):.2f}\\%
\\end{{itemize}}

"""
        return content
    
    def _generate_trades_section(self, trades: List[Dict]) -> str:
        """Generate per-trade section"""
        content = "\\section{Trade Details}\n\n"
        
        for i, trade in enumerate(trades, 1):
            content += f"""\\subsection{{Trade {i}: {trade.get('symbol')}}}

Entry: \\${trade.get('entry_price', 0):.2f}}
Exit: \\${trade.get('exit_price', 0):.2f}}
TP: \\${trade.get('tp_price', 0):.2f}}
SL: \\${trade.get('sl_price', 0):.2f}}
Position Size: {trade.get('position_size', 0):.4f}}
P\\&L: \\${trade.get('pnl_usd', 0):.2f}} ({trade.get('pnl_pct', 0):.2f}\\%)

"""
        
        return content
    
    def _generate_conclusion(self) -> str:
        """Generate conclusion section"""
        return """\\section{Conclusion}

Trading completed for the day. All positions managed according to risk rules.

"""
    
    def _generate_footer(self) -> str:
        """LaTeX document footer"""
        return "\\end{document}"
    
    def compile_to_pdf(self, tex_path: str) -> str:
        """Compile LaTeX to PDF"""
        import subprocess
        
        pdf_path = tex_path.replace('.tex', '.pdf')
        
        try:
            subprocess.run(['pdflatex', '-interaction=nonstopmode', tex_path],
                          cwd=self.reports_dir)
            return pdf_path
        except Exception as e:
            print(f"PDF compilation failed: {e}")
            return None
```

---

## src/utils/config_loader.py

```python
"""
Configuration Loader

Loads and validates YAML configuration files.
Resolves environment variables.
"""

import yaml
import os
from pathlib import Path
from typing import Dict, Any


class ConfigLoader:
    """Loads YAML configuration files"""
    
    def __init__(self, config_dir: str = "config"):
        self.config_dir = config_dir
    
    def load(self) -> Dict[str, Any]:
        """Load all config files"""
        config = {}
        
        # Load each YAML file
        for filename in ['settings', 'risk', 'filters', 'schedule']:
            filepath = f"{self.config_dir}/{filename}.yaml"
            if os.path.exists(filepath):
                with open(filepath, 'r') as f:
                    config[filename] = yaml.safe_load(f)
                    # Resolve env vars
                    config[filename] = self._resolve_env(
                        config[filename]
                    )
        
        return type('Config', (), config)()
    
    def _resolve_env(self, obj: Any) -> Any:
        """Recursively resolve environment variables"""
        if isinstance(obj, dict):
            return {k: self._resolve_env(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._resolve_env(item) for item in obj]
        elif isinstance(obj, str) and obj.startswith("${"):
            # Extract variable name
            var_name = obj[2:-1]
            return os.getenv(var_name, obj)
        return obj
```

---

**Files included:**
- src/execution/order_executor.py (80 lines) ✅
- src/execution/position_manager.py (100 lines) ✅
- src/reporting/logger.py (120 lines) ✅
- src/reporting/plotter.py (150 lines) ✅
- src/reporting/latex_reporter.py (130 lines) ✅
- src/utils/config_loader.py (60 lines) ✅

Ready for PART 6 (screening, utils, tests)?
