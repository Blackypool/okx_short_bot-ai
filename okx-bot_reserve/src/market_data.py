import pandas as pd
import os
from api_client import OKXClient

class MarketDataManager:
    def __init__(self, api_client: OKXClient):
        self.api = api_client
        self.cache_dir = 'data/historical'
        os.makedirs(self.cache_dir, exist_ok=True)
    
    def get_ohlcv(self, symbol: str, timeframe: str = '15m', lookback: int = 300) -> pd.DataFrame:
        cache_file = f"{self.cache_dir}/{symbol.replace('-', '_')}_{timeframe}.csv"
        
        candles = self.api.get_klines(symbol, timeframe, lookback)
        if not candles:
            return pd.DataFrame()
        
        df = pd.DataFrame(candles, columns=['ts','o','h','l','c','vol','volCcy','volCcyQuote','confirm'])
        df = df[['ts','o','h','l','c','vol']].copy()
        df[['o','h','l','c','vol']] = df[['o','h','l','c','vol']].astype(float)
        df['ts'] = pd.to_datetime(df['ts'], unit='ms')
        df = df.sort_values('ts').reset_index(drop=True)
        df.to_csv(cache_file, index=False)
        return df
