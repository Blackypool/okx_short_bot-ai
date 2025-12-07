import yaml, os
from dotenv import load_dotenv

load_dotenv()

class ConfigLoader:
    def __init__(self, config_dir='config'):
        self.config_dir = config_dir
    
    def load(self):
        config = {}
        for file in ['settings.yaml', 'risk.yaml', 'filters.yaml', 'schedule.yaml']:
            path = f"{self.config_dir}/{file}"
            if os.path.exists(path):
                with open(path) as f:
                    section = yaml.safe_load(f)
                    config.update(section)
        
        config['exchange'] = {
            'apikey': os.getenv('OKXAPIKEY'),
            'apisecret': os.getenv('OKXAPISECRET'),
            'passphrase': os.getenv('OKXPASSPHRASE')
        }
        return config
