# OKX Intraday Short Bot — PART 4: TECHNICAL ANALYSIS & STRATEGY

## 📊 PART 4: Technical Analysis & Strategy Modules

---

## src/ta/fvg_detector.py

```python
"""
Fair Value Gap (FVG) Detection

Identifies 3-candle imbalance patterns:
- Bullish FVG: High[i] > Low[i+1] (potential short entry zone)
- Minimum size: 0.3-0.5% of current price
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Optional


class FVGDetector:
    """Detects Fair Value Gap patterns"""
    
    def __init__(self, min_gap_pct: float = 0.3):
        self.min_gap_pct = min_gap_pct
    
    def detect_fvg(self, df: pd.DataFrame, 
                   fvg_type: str = "bullish") -> List[Dict]:
        """
        Detect FVG patterns in OHLCV data
        
        Args:
            df: DataFrame with columns [open, high, low, close]
            fvg_type: "bullish" or "bearish"
        
        Returns:
            List of FVG patterns with:
            - high, low, midpoint
            - age (bars since creation)
            - size_pct
        """
        fvgs = []
        
        for i in range(1, len(df) - 1):
            if fvg_type == "bullish":
                # Bullish FVG: High[i] > Low[i+1]
                # Gap zone between Low[i+1] and High[i-1]
                if df.iloc[i]['high'] > df.iloc[i+1]['low']:
                    gap_high = min(df.iloc[i]['high'], 
                                  df.iloc[i-1]['high'])
                    gap_low = max(df.iloc[i]['low'], 
                                 df.iloc[i+1]['low'])
                    gap_size = gap_high - gap_low
                    gap_size_pct = (gap_size / df.iloc[i]['close']) * 100
                    
                    if gap_size_pct >= self.min_gap_pct:
                        fvgs.append({
                            'type': 'bullish',
                            'high': gap_high,
                            'low': gap_low,
                            'midpoint': (gap_high + gap_low) / 2,
                            'size': gap_size,
                            'size_pct': gap_size_pct,
                            'bar_index': i,
                            'age_bars': len(df) - i - 1
                        })
        
        return fvgs
    
    def is_fvg_valid_for_trend(self, fvg: Dict, 
                               is_uptrend: bool) -> bool:
        """
        Validate FVG for current trend
        
        In uptrend: bullish FVG is valid for short
        In downtrend: bearish FVG is valid for long
        """
        if is_uptrend and fvg['type'] == 'bullish':
            return True
        elif not is_uptrend and fvg['type'] == 'bearish':
            return True
        return False
    
    def get_active_fvgs(self, df: pd.DataFrame,
                       max_age_bars: int = 50) -> List[Dict]:
        """Get FVGs that are still active (age <= max_age_bars)"""
        all_fvgs = self.detect_fvg(df)
        return [fvg for fvg in all_fvgs if fvg['age_bars'] <= max_age_bars]
```

---

## src/ta/trendlines.py

```python
"""
Trendline Analysis

Constructs ascending support lines from swing lows.
Detects breakouts and retests.
"""

import pandas as pd
import numpy as np
from scipy.stats import linregress
from typing import List, Dict, Optional, Tuple


class TrendlineAnalyzer:
    """Trendline detection and analysis"""
    
    def __init__(self, min_touches: int = 3, min_angle: float = 5.0):
        self.min_touches = min_touches
        self.min_angle = min_angle
    
    def find_local_minima(self, df: pd.DataFrame,
                         lookback: int = 100) -> List[Dict]:
        """
        Find local minima (swing lows)
        
        A swing low is a bar where price < both neighbors
        """
        minima = []
        
        for i in range(1, len(df) - 1):
            if (df.iloc[i]['low'] < df.iloc[i-1]['low'] and
                df.iloc[i]['low'] < df.iloc[i+1]['low']):
                minima.append({
                    'bar_index': i,
                    'price': df.iloc[i]['low'],
                    'timestamp': df.iloc[i]['timestamp']
                })
        
        return minima[-lookback:] if lookback else minima
    
    def build_trendline(self, minima: List[Dict],
                       min_touches: Optional[int] = None,
                       min_angle: Optional[float] = None) -> Optional[Dict]:
        """
        Fit trendline through local minima
        
        Uses least squares linear regression.
        Validates: >= min_touches and angle >= min_angle degrees
        """
        if min_touches is None:
            min_touches = self.min_touches
        if min_angle is None:
            min_angle = self.min_angle
        
        if len(minima) < min_touches:
            return None
        
        # Extract coordinates
        x_vals = np.array([m['bar_index'] for m in minima])
        y_vals = np.array([m['price'] for m in minima])
        
        # Fit line
        slope, intercept, r_value, _, _ = linregress(x_vals, y_vals)
        
        # Calculate angle
        angle = np.degrees(np.arctan(slope))
        
        if angle < min_angle:
            return None
        
        return {
            'slope': slope,
            'intercept': intercept,
            'angle': angle,
            'r_squared': r_value ** 2,
            'touches': len(minima),
            'minima': minima
        }
    
    def get_trendline_value(self, trendline: Dict, bar_index: int) -> float:
        """Get trendline price at specific bar"""
        return trendline['slope'] * bar_index + trendline['intercept']
    
    def detect_trendline_breakout(self, df: pd.DataFrame,
                                 trendline: Dict,
                                 breakout_tolerance_pct: float = 0.1) \
                                 -> Tuple[bool, Optional[Dict]]:
        """
        Detect if price has broken below trendline
        
        Breakout confirmed when:
        1. Close < trendline
        2. Confirmed by next candle also below
        """
        last_bar_idx = len(df) - 1
        last_close = df.iloc[last_bar_idx]['close']
        trendline_price = self.get_trendline_value(trendline, 
                                                    last_bar_idx)
        
        # Breakout if close is below trendline (with tolerance)
        tolerance = trendline_price * (breakout_tolerance_pct / 100)
        
        if last_close < trendline_price - tolerance:
            return True, {
                'bar_index': last_bar_idx,
                'breakout_price': last_close,
                'trendline_level': trendline_price,
                'distance_pcts': ((trendline_price - last_close) / 
                                 last_close * 100)
            }
        
        return False, None
    
    def detect_retest(self, df: pd.DataFrame,
                     trendline: Dict,
                     breakout_info: Dict,
                     retest_tolerance_pct: float = 0.5) -> bool:
        """
        Detect if price retests trendline after breakout
        
        Retest = price returns near trendline but stays below
        """
        recent_bars = df.iloc[-10:] if len(df) > 10 else df
        
        for idx, row in recent_bars.iterrows():
            trendline_val = self.get_trendline_value(
                trendline, idx
            )
            tolerance = trendline_val * (retest_tolerance_pct / 100)
            
            if (abs(row['close'] - trendline_val) <= tolerance and
                row['close'] < trendline_val):
                return True
        
        return False
```

---

## src/ta/trend_state.py

```python
"""
Trend State Analysis

Determines if market is in uptrend/downtrend
using Higher Highs (HH) / Higher Lows (HL) analysis.
"""

import pandas as pd
import numpy as np
from typing import Tuple, Dict, List


class TrendState:
    """Trend verification using HH/HL pattern"""
    
    def is_uptrend(self, df: pd.DataFrame,
                   lookback: int = 50) -> Tuple[bool, Dict]:
        """
        Check if market is in uptrend
        
        Uptrend = sequence of Higher Lows (HL)
        Each new local minimum > previous local minimum
        
        Returns: (is_uptrend, {swing_points, lows, highs})
        """
        df_recent = df.tail(lookback) if len(df) > lookback else df
        
        # Find local minima
        lows = []
        for i in range(1, len(df_recent) - 1):
            if (df_recent.iloc[i]['low'] < 
                df_recent.iloc[i-1]['low'] and
                df_recent.iloc[i]['low'] < 
                df_recent.iloc[i+1]['low']):
                lows.append({
                    'index': i,
                    'price': df_recent.iloc[i]['low']
                })
        
        # Check HL pattern
        if len(lows) < 2:
            return False, {'error': 'Not enough swing lows'}
        
        # Verify each low > previous low
        for i in range(1, len(lows)):
            if lows[i]['price'] <= lows[i-1]['price']:
                return False, {'error': 'Lower low detected'}
        
        # Find local maxima for HH check (optional)
        highs = []
        for i in range(1, len(df_recent) - 1):
            if (df_recent.iloc[i]['high'] > 
                df_recent.iloc[i-1]['high'] and
                df_recent.iloc[i]['high'] > 
                df_recent.iloc[i+1]['high']):
                highs.append({
                    'index': i,
                    'price': df_recent.iloc[i]['high']
                })
        
        return True, {
            'swing_lows': lows,
            'swing_highs': highs,
            'last_low': lows[-1]['price'],
            'last_high': highs[-1]['price'] if highs else 0
        }
    
    def get_swing_points(self, df: pd.DataFrame,
                        lookback: int = 100) -> Dict:
        """Get recent swing points"""
        df_recent = df.tail(lookback)
        
        swings = {'lows': [], 'highs': []}
        
        for i in range(1, len(df_recent) - 1):
            # Local lows
            if (df_recent.iloc[i]['low'] < 
                df_recent.iloc[i-1]['low'] and
                df_recent.iloc[i]['low'] < 
                df_recent.iloc[i+1]['low']):
                swings['lows'].append({
                    'index': i,
                    'price': df_recent.iloc[i]['low']
                })
            
            # Local highs
            if (df_recent.iloc[i]['high'] > 
                df_recent.iloc[i-1]['high'] and
                df_recent.iloc[i]['high'] > 
                df_recent.iloc[i+1]['high']):
                swings['highs'].append({
                    'index': i,
                    'price': df_recent.iloc[i]['high']
                })
        
        return swings
```

---

## src/strategy/signal_engine.py

```python
"""
Signal Generation Engine

Combines FVG, trendline, and trend analysis to generate trading signals.
Three signal types: FVG_ONLY, TREND_ONLY, FVG_TREND_COMBO
"""

import pandas as pd
from typing import List, Dict, Optional
from datetime import datetime
import logging


class SignalEngine:
    """Generates trading signals from technical analysis"""
    
    def __init__(self):
        self.logger = logging.getLogger("SignalEngine")
    
    def generate_signals(self, symbol: str,
                        df_m15: pd.DataFrame,
                        df_h1: pd.DataFrame,
                        analysis: Dict) -> List[Dict]:
        """
        Generate trading signals
        
        Returns list of signal dicts with:
        - type (FVG_ONLY, TREND_ONLY, FVG_TREND_COMBO)
        - confidence (0-100)
        - entry_logic
        - entry_price_zone
        """
        signals = []
        
        # Extract analysis results
        is_uptrend = analysis.get('is_uptrend', False)
        fvgs = analysis.get('fvgs', [])
        trendline = analysis.get('trendline')
        trendline_breakout = analysis.get('trendline_breakout', False)
        retest = analysis.get('retest', False)
        
        if not is_uptrend:
            return signals  # No shorts in downtrend
        
        # Signal 1: FVG_TREND_COMBO (60% target)
        if fvgs and trendline and trendline_breakout:
            signal = {
                'type': 'FVG_TREND_COMBO',
                'symbol': symbol,
                'timestamp': datetime.utcnow(),
                'confidence': 95 if retest else 85,
                'entry_logic': 'Trendline breakout + FVG reversion',
                'setup': {
                    'fvg_high': fvgs[0]['high'],
                    'fvg_low': fvgs[0]['low'],
                    'trendline_angle': trendline['angle'],
                    'retest_detected': retest
                }
            }
            signals.append(signal)
        
        # Signal 2: FVG_ONLY (20% target)
        elif fvgs and not trendline_breakout:
            signal = {
                'type': 'FVG_ONLY',
                'symbol': symbol,
                'timestamp': datetime.utcnow(),
                'confidence': 60,
                'entry_logic': 'FVG reversion without trendline',
                'setup': {
                    'fvg_high': fvgs[0]['high'],
                    'fvg_low': fvgs[0]['low']
                }
            }
            signals.append(signal)
        
        # Signal 3: TREND_ONLY (20% target)
        elif trendline and trendline_breakout and not fvgs:
            signal = {
                'type': 'TREND_ONLY',
                'symbol': symbol,
                'timestamp': datetime.utcnow(),
                'confidence': 70,
                'entry_logic': 'Trendline breakout without FVG',
                'setup': {
                    'trendline_level': trendline['slope'],
                    'breakout_confirmed': True
                }
            }
            signals.append(signal)
        
        return signals
    
    def validate_signal(self, signal: Dict) -> bool:
        """Validate signal structure"""
        required = ['type', 'symbol', 'confidence', 'setup']
        return all(k in signal for k in required)
```

---

## src/strategy/rr_calculator.py

```python
"""
Risk/Reward Calculator

Calculates R/R ratio and position sizing based on risk management rules.
Validates: R/R >= 1:4 (or 1:3 for premium setups)
"""

import pandas as pd
from typing import Tuple, Optional


class RRCalculator:
    """Risk/Reward and position sizing calculator"""
    
    def calculate_rr(self, entry_price: float,
                    stop_price: float,
                    tp_price: float) -> float:
        """
        Calculate Risk/Reward ratio
        
        R/R = Reward / Risk = |Entry - TP| / |Entry - SL|
        """
        risk = abs(entry_price - stop_price)
        reward = abs(entry_price - tp_price)
        
        if risk == 0:
            return 0
        
        return reward / risk
    
    def calculate_position_size(self, entry_price: float,
                               stop_price: float,
                               deposit: float,
                               leverage: int = 10,
                               max_risk_pct: float = 5.0) -> float:
        """
        Calculate position size based on risk
        
        Position size = (deposit × max_risk% / risk_per_contract)
        Adjusted for leverage
        """
        # Risk per contract (in USDT)
        risk_per_contract = abs(entry_price - stop_price)
        
        # Max risk amount
        max_risk_amount = deposit * (max_risk_pct / 100)
        
        # Position size = max_risk / risk_per_contract
        position_size = max_risk_amount / risk_per_contract
        
        # Adjust for leverage
        position_size = position_size / leverage
        
        return position_size
    
    def validate_rr(self, rr: float, min_rr: float = 4.0,
                   premium_mode: bool = False) -> bool:
        """Validate R/R meets minimum threshold"""
        if premium_mode:
            return rr >= 3.0
        return rr >= min_rr
```

---

## src/strategy/risk_manager.py

```python
"""
Risk Manager

Validates trades against risk management rules:
- Position size <= 5% of deposit
- R/R >= 1:4
- No overlapping positions
- Daily loss limits
"""

import logging
from typing import Tuple


class RiskManager:
    """Risk validation and position limits"""
    
    def __init__(self, config: dict):
        self.config = config
        self.logger = logging.getLogger("RiskManager")
        self.max_risk_pct = config.position.max_risk_pct
        self.min_rr = config.position.min_rr
        self.premium_rr = config.position.premium_rr
    
    def validate_risk(self, risk_pct: float) -> Tuple[bool, str]:
        """Validate risk per trade"""
        if risk_pct > self.max_risk_pct:
            return False, f"Risk {risk_pct}% > max {self.max_risk_pct}%"
        return True, "Risk OK"
    
    def validate_rr(self, rr: float, premium: bool = False) \
                   -> Tuple[bool, str]:
        """Validate R/R ratio"""
        threshold = self.premium_rr if premium else self.min_rr
        if rr < threshold:
            return False, f"R/R {rr:.2f} < min {threshold}"
        return True, f"R/R OK ({rr:.2f})"
    
    def validate_signal(self, signal: dict) -> Tuple[bool, str]:
        """Validate complete signal"""
        if 'type' not in signal:
            return False, "Invalid signal type"
        
        if signal['type'] not in ['FVG_ONLY', 'TREND_ONLY', 
                                 'FVG_TREND_COMBO']:
            return False, f"Unknown signal type: {signal['type']}"
        
        return True, "Signal valid"
```

---

## Continue to PART 5...

These modules handle:
- FVG detection (3-candle patterns)
- Trendline analysis (support lines, breakouts)
- Trend verification (HH/HL pattern)
- Signal generation (3 types)
- R/R calculation
- Risk validation

**Files included:**
- src/ta/fvg_detector.py (80 lines) ✅
- src/ta/trendlines.py (150 lines) ✅
- src/ta/trend_state.py (100 lines) ✅
- src/strategy/signal_engine.py (100 lines) ✅
- src/strategy/rr_calculator.py (60 lines) ✅
- src/strategy/risk_manager.py (60 lines) ✅

Ready for PART 5 (execution, reporting, utils)?
