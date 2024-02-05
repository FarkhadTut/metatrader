import configparser
import os

ROOT = os.getcwd()
FILENAME = 'config.ini'


class TradeConfig():
    def __init__(self) -> None:
        self.config = configparser.ConfigParser()
        self.config_path = os.path.join(ROOT, 'config', FILENAME)
        self.config.read(self.config_path)
    

    def get_config(self):
        self.config_path = os.path.join(ROOT, 'config', FILENAME)
        self.config.read(self.config_path)
        return self.config
    
    @property
    def lot(self):
        return float(self.get_config()['TRADING']['lot'])

    @property
    def stop_loss(self):
        return float(self.get_config()['TRADING']['stop_loss'])
    
    @property
    def symbol(self):
        return self.get_config()['TRADING']['symbol']
    
    @property
    def deviation(self):
        return int(self.get_config()['TRADING']['deviation'])
    
    @property
    def max_ticks(self):
        return int(self.get_config()['DATA']['max_ticks'])

    @property
    def account(self):
        login =  self.get_config()['ACCOUNT']['login']
        password =  self.get_config()['ACCOUNT']['password']
        server =  self.get_config()['ACCOUNT']['server']

        return {
            'login': int(login),
            'password': password,
            'server': server,
        }
    @property
    def start_year(self):
        return int(self.get_config()['MODEL']['start_year'])


