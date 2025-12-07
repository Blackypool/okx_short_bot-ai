import json
import logging
from datetime import datetime

class TradeLogger:
    def __init__(self):
        self.logger = logging.getLogger('TradeLogger')
    
    def log_signal(self, signal_data: dict):
        filename = f"logs/signals_{datetime.now().strftime('%Y%m%d')}.json"
        with open(filename, 'a') as f:
            json.dump(signal_data, f)
            f.write('\n')
        self.logger.info(f'💾 Signal logged: {signal_data["symbol"]}')
    
    def log_trade(self, trade_data: dict):
        filename = f"logs/trades_{datetime.now().strftime('%Y%m%d')}.json"
        with open(filename, 'a') as f:
            json.dump(trade_data, f)
            f.write('\n')
        self.logger.info(f'💰 Trade logged: {trade_data["symbol"]}')
