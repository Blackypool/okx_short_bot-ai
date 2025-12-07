import pandas as pd
import numpy as np
from typing import List, Dict

class TrendAnalyzer:
    def build_trendlines(self, df: pd.DataFrame) -> List[Dict]:
        """Ascending support trendlines (PART_4)"""
        lows = df['l'].rolling(window=10).min()
        local_mins = []
        
        for i in range(10, len(df)-10):
            if df['l'].iloc[i] == lows.iloc[i]:
                local_mins.append((i, float(df['l'].iloc[i])))
        
        trendlines = []
        if len(local_mins) >= 2:
            x1, y1 = local_mins[-2]
            x2, y2 = local_mins[-1]
            slope = (y2 - y1) / (x2 - x1)
            trendlines.append({
                'slope': slope,
                'points': local_mins[-2:],
                'is_uptrend': slope > 0
            })
        return trendlines
