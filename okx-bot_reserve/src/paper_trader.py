import logging

class PaperTradingSimulator:
    def __init__(self, initial_balance: float = 1000.0):
        self.balance = initial_balance
        self.equity = initial_balance
        self.positions = {}
        self.trades = []
        self.logger = logging.getLogger('PaperTrader')
    
    def open_position(self, symbol: str, entry: float, size: float = 1.0):
        self.positions[symbol] = {'entry': entry, 'size': size}
        self.logger.info(f'📄 PAPER: Open {symbol} @ {entry:.4f}')
    
    def close_position(self, symbol: str, exit_price: float):
        if symbol in self.positions:
            pos = self.positions[symbol]
            pnl = (pos['entry'] - exit_price) * pos['size']
            self.equity += pnl
            self.trades.append({'symbol': symbol, 'entry': pos['entry'], 'exit': exit_price, 'pnl': pnl})
            del self.positions[symbol]
            self.logger.info(f'📄 PAPER: Close {symbol} PnL:{pnl:.2f}')
