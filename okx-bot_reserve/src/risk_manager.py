class RiskManager:
    def __init__(self, config):
        self.max_risk_pct = config.get('risk', {}).get('maxriskpct', 5.0) / 100
        self.min_rr = config.get('risk', {}).get('minrr', 4.0)
        self.leverage = config.get('risk', {}).get('leverage', 10)
    
    def validate_trade(self, entry: float, sl: float, tp: float) -> bool:
        risk = abs(entry - sl) / entry
        reward = abs(tp - entry) / entry
        rr = reward / risk if risk > 0 else 0
        return rr >= self.min_rr and risk <= self.max_risk_pct
    
    def calculate_position_size(self, balance: float, entry: float, sl: float) -> float:
        risk_amount = balance * self.max_risk_pct
        risk_per_unit = abs(entry - sl) / entry
        return risk_amount / risk_per_unit if risk_per_unit > 0 else 0
