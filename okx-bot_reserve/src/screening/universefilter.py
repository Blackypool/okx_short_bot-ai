class UniverseFilter:
    def __init__(self, config):
        self.min_volume = config.get('filters', {}).get('minvolumeusd', 25000000)

    def get_eligible_symbols(self):
        return [
            'BTC-USDT-SWAP', 'ETH-USDT-SWAP', 'SOL-USDT-SWAP', 'BNB-USDT-SWAP',
            'XRP-USDT-SWAP', 'DOGE-USDT-SWAP', 'ADA-USDT-SWAP', 'TRX-USDT-SWAP', 
            'AVAX-USDT-SWAP', 'SHIB-USDT-SWAP', 'LINK-USDT-SWAP', 'DOT-USDT-SWAP'
        ]
