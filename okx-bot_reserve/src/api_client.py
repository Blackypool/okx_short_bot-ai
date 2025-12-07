import requests
from typing import List

class OKXClient:
    BASE_URL = 'https://www.okx.com'
    
    def __init__(self, config):
        self.api_key = config['exchange']['apikey']
    
    def get_klines(self, inst_id: str, bar: str = '15m', limit: int = 300) -> List[List]:
        endpoint = '/api/v5/market/candles'
        params = {'instId': inst_id, 'bar': bar, 'limit': str(limit)}
        url = f"{self.BASE_URL}{endpoint}?{'&'.join([f'{k}={v}' for k,v in params.items()])}"
        response = requests.get(url)
        data = response.json()
        return data.get('data', []) if data.get('code') == '0' else []
