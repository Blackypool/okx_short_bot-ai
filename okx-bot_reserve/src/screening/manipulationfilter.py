import pandas as pd
import numpy as np

class ManipulationFilter:
    def __init__(self, config):
        self.lookback_days = config.get('filters', {}).get('lookbackdays', 3)
    
    def is_manipulation_asset(self, symbol, df):
        if len(df) < 50:
            return False
        
        # Wick analysis (слишком длинные тени = манипуляция)
        body_size = abs(df['close'] - df['open'])
        upper_wick = df['high'] - np.maximum(df['close'], df['open'])
        lower_wick = np.minimum(df['close'], df['open']) - df['low']
        
        wick_ratio = (upper_wick + lower_wick) / (body_size + 1e-8)
        manipulation_wicks = (wick_ratio > 3).sum()
        
        return manipulation_wicks > 5  # 5+ манипулятивных свечей
