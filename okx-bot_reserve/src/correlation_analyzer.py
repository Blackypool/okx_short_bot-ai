import pandas as pd
import numpy as np
import requests

class CorrelationAnalyzer:
    def __init__(self):
        self.btc_cache = None
    
    def get_btc_data(self):
        if self.btc_cache is not None:
            return self.btc_cache
        url = "https://www.okx.com/api/v5/market/candles?instId=BTC-USDT-SWAP&bar=15m&limit=300"
        data = requests.get(url).json()
        if data['code'] == '0':
            df = pd.DataFrame(data['data'], columns=['ts','o','h','l','c','vol','volCcy','volCcyQuote','confirm'])
            df = df[['ts','o','h','l','c']].copy()
            df[['o','h','l','c']] = df[['o','h','l','c']].astype(float)
            self.btc_cache = df.sort_values('ts').reset_index(drop=True)
            return self.btc_cache
        return pd.DataFrame()
    
    def calculate_correlation(self, symbol_df):
        btc_df = self.get_btc_data()
        if len(symbol_df) < 50 or len(btc_df) < 50:
            return 0.5
        
        symbol_ret = symbol_df['c'].pct_change().dropna()
        btc_ret = btc_df['c'].pct_change().dropna()
        min_len = min(len(symbol_ret), len(btc_ret))
        corr = symbol_ret.tail(min_len).corr(btc_ret.tail(min_len))
        return abs(corr) if not pd.isna(corr) else 0.5
