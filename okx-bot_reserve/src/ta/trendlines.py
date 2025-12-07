import pandas as pd
import numpy as np
from typing import List, Dict

class TrendlineAnalyzer:
    def build_trendline(self, df: pd.DataFrame) -> List[Dict]:
        lows = df['low'].rolling(window=10).min()
        local_mins = []
        
        for i in range(10, len(df)-10):
            if df['low'].iloc[i] == lows.iloc[i]:
                local_mins.append((i, float(df['low'].iloc[i])))
        
        trendlines = []
        if len(local_mins) >= 2:
            x1, y1 = local_mins[-2]
            x2, y2 = local_mins[-1]
            slope = (y2 - y1) / (x2 - x1)
            trendlines.append({'slope': slope, 'points': local_mins[-2:]})
        
        return trendlines
