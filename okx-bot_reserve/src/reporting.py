import json
from datetime import datetime

class Reporter:
    def log_signal(self, symbol, entry, sl, tp, fvgs):
        signal = {
            'timestamp': datetime.now().isoformat(),
            'symbol': symbol,
            'entry': entry,
            'sl': sl,
            'tp': tp,
            'fvgs': len(fvgs),
            'rr': (entry-tp)/(sl-entry)
        }
        with open(f'logs/signals_{datetime.now().strftime("%Y%m%d")}.json', 'a') as f:
            json.dump(signal, f)
            f.write('\n')
