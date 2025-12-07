import pandas as pd
from typing import List, Dict

class FVGDetector:
    def detect_fvgs(self, df: pd.DataFrame) -> List[Dict]:
        fvgs = []
        for i in range(2, len(df)):
            prev_high = df['high'].iloc[i-2]
            curr_low = df['low'].iloc[i]
            gap_size = curr_low - prev_high
            if gap_size > 0.0001 * df['close'].iloc[i]:
                fvgs.append({
                    'index': i,
                    'type': 'bullish',
                    'top': curr_low,
                    'bottom': prev_high,
                    'gap_size': gap_size
                })
        return fvgs
