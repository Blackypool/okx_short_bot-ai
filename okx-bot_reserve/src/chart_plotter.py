import matplotlib.pyplot as plt
import logging
from datetime import datetime

class ChartPlotter:
    def __init__(self):
        self.logger = logging.getLogger('ChartPlotter')
    
    def plot_signal(self, df, symbol: str, entry: float, sl: float, tp: float):
        filename = f"reports/charts/{symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        plt.figure(figsize=(12, 6))
        plt.plot(df['c'], label='Close')
        plt.axhline(entry, color='g', label=f'Entry:{entry:.4f}')
        plt.axhline(sl, color='r', label=f'SL:{sl:.4f}')
        plt.axhline(tp, color='b', label=f'TP:{tp:.4f}')
        plt.legend()
        plt.title(f'{symbol} - SHORT SIGNAL')
        plt.savefig(filename)
        plt.close()
        self.logger.info(f'📊 Chart saved: {filename}')
