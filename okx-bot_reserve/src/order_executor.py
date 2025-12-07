import logging

class OrderExecutor:
    def __init__(self, api_client):
        self.api = api_client
        self.logger = logging.getLogger('OrderExecutor')
    
    def place_short_order(self, symbol: str, size: float, entry: float):
        self.logger.info(f'📈 PLACE SHORT: {symbol} Size:{size:.4f} Entry:{entry:.4f}')
        # В livetrade: self.api.place_order(symbol, 'sell', 'market', size)
    
    def place_tp_sl(self, symbol: str, tp: float, sl: float):
        self.logger.info(f'⚠️  TP/SL: {symbol} TP:{tp:.4f} SL:{sl:.4f}')
    
    def close_position(self, symbol: str):
        self.logger.info(f'❌ CLOSE: {symbol}')
