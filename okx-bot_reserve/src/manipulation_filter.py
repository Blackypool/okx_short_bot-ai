import pandas as pd
import numpy as np

class ManipulationFilter:
    def __init__(self, wick_threshold=3.0, anomaly_threshold=5):
        self.wick_threshold = wick_threshold
        self.anomaly_threshold = anomaly_threshold
        self.banned = {}
    
    def is_clean(self, df: pd.DataFrame) -> bool:
        if len(df) < 50:
            return True
        
        body = abs(df['c'] - df['o'])
        upper_wick = df['h'] - np.maximum(df['o'], df['c'])
        lower_wick = np.minimum(df['o'], df['c']) - df['l']
        total_wick = upper_wick + lower_wick
        
        wick_ratio = total_wick / (body + 1e-8)
        anomalies = (wick_ratio > self.wick_threshold).sum()
        
        return anomalies < self.anomaly_threshold
