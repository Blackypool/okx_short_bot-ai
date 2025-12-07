import pandas as pd
import numpy as np
import requests

class CorrelationFilter:
    def __init__(self, max_corr=0.2):
        self.max_corr = max_corr
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
    
    def is_low_correlation(self, symbol_df: pd.DataFrame) -> bool:
        btc_df = self.get_btc_data()
        if len(symbol_df) < 50 or len(btc_df) < 50:
            return True
        
        symbol_ret = symbol_df['c'].pct_change().dropna()
        btc_ret = btc_df['c'].pct_change().dropna()
        min_len = min(len(symbol_ret), len(btc_ret))
        corr = abs(symbol_ret.tail(min_len).corr(btc_ret.tail(min_len)))
        return corr < self.max_corr if not pd.isna(corr) else True
