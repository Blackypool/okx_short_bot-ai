class RiskManager:
    def __init__(self, config):
        self.max_risk_pct = config.get('risk', {}).get('maxriskpct', 5.0)
        self.min_rr = config.get('risk', {}).get('minrr', 4.0)
        self.leverage = config.get('risk', {}).get('leverage', 10)
    
    def validate_signal(self, symbol, entry, sl, tp):
        risk = abs(entry - sl) / entry
        reward = abs(tp - entry) / entry
        rr = reward / risk
        
        return rr >= self.min_rr and risk <= self.max_risk_pct / 100
