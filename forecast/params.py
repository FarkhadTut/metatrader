import configparser
import os

ROOT = os.getcwd()
FILENAME = 'config.ini'


class ModelParams():
    def __init__(self) -> None:
        self.config = configparser.ConfigParser()
        self.config_path = os.path.join(ROOT, 'config', FILENAME)
        self.config.read(self.config_path)

    def get_config(self):
        self.config_path = os.path.join(ROOT, 'config', FILENAME)
        self.config.read(self.config_path)
        return self.config

    @property
    def lags(self):
        return int(self.get_config()['MODEL']['lags'])

    @property
    def diff_order(self):
        return int(self.get_config()['MODEL']['diff_order'])
    
    @property
    def steps(self):
        return int(self.get_config()['MODEL']['steps'])
    
    @property
    def target_column(self):
        return self.get_config()['MODEL']['target_column']
    
