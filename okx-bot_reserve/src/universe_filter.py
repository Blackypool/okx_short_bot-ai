import requests
import logging

logger = logging.getLogger('UniverseFilter')

class UniverseFilter:
    def get_symbols(self, min_volume_usd=5000000):  # $5M+ для больше пар
        """ТОП 200+ по объёму 24h (PART_6)"""
        try:
            url = "https://www.okx.com/api/v5/market/tickers?instType=SWAP"
            data = requests.get(url, timeout=10).json()
            
            if data['code'] != '0':
                logger.warning('API error, fallback symbols')
                return ['BTC-USDT-SWAP','ETH-USDT-SWAP','SOL-USDT-SWAP','BNB-USDT-SWAP']
            
            symbols = []
            for ticker in data['data']:
                symbol = ticker['instId']
                vol_usd = float(ticker.get('volCcy24h', 0))
                
                # Только USDT perpetual swaps с объёмом > $5M
                if (vol_usd > min_volume_usd and 
                    symbol.endswith('-USDT-SWAP') and 
                    'BTC' not in symbol):  # Исключаем BTC
                    
                    symbols.append(symbol)
            
            symbols = symbols[:200]  # ТОП 200
            logger.info(f'✅ Universe: {len(symbols)} pairs (Vol>${min_volume_usd:,})')
            return symbols
            
        except Exception as e:
            logger.error(f'Universe error: {e}')
            return ['ETH-USDT-SWAP','SOL-USDT-SWAP','BNB-USDT-SWAP','XRP-USDT-SWAP']
