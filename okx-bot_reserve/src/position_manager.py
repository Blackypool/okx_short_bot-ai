import logging
from datetime import datetime, timedelta

class PositionManager:
    def __init__(self, config):
        self.positions = {}
        self.max_positions = config.get('risk', {}).get('maxpositions', 5)
        self.position_timeout = config.get('risk', {}).get('positiontimeout', 24)
        self.logger = logging.getLogger('PositionManager')
    
    def open_position(self, symbol: str, entry: float, sl: float, tp: float):
        if len(self.positions) >= self.max_positions:
            self.logger.warning('Max positions reached!')
            return False
        
        self.positions[symbol] = {
            'entry': entry,
            'sl': sl,
            'tp': tp,
            'open_time': datetime.now(),
            'status': 'open'
        }
        self.logger.info(f'✅ OPEN: {symbol} @ {entry:.4f}')
        return True
    
    def close_position(self, symbol: str, exit_price: float):
        if symbol in self.positions:
            pos = self.positions[symbol]
            pnl = (pos['entry'] - exit_price) * 1  # size=1
            self.logger.info(f'✅ CLOSE: {symbol} PnL:{pnl:.2f}')
            del self.positions[symbol]
    
    def check_timeouts(self):
        now = datetime.now()
        for symbol, pos in list(self.positions.items()):
            elapsed = (now - pos['open_time']).total_seconds() / 3600
            if elapsed > self.position_timeout:
                self.logger.warning(f'⏱️  TIMEOUT: {symbol} - {elapsed:.1f}h')
                self.close_position(symbol, pos['entry'])
