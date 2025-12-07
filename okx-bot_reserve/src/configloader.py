import yaml
import os
from dotenv import load_dotenv

load_dotenv()

class ConfigLoader:
    def __init__(self, config_path):
        self.config_path = config_path
    
    def load(self):
        config = {
            'exchange': {
                'apikey': os.getenv('OKXAPIKEY'),
                'apisecret': os.getenv('OKXAPISECRET'),
                'passphrase': os.getenv('OKXPASSPHRASE')
            },
            'filters': {'maxcorr': 0.2},
            'risk': {'maxriskpct': 5.0, 'minrr': 4.0}
        }
        return config
