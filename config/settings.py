import configparser
import os
config = configparser.ConfigParser()
ROOT = os.getcwd()
FILENAME = 'config.ini'



def get_settings():
    config_path = os.path.join(ROOT, 'config', FILENAME)
    config.read(config_path)
    return config

def lot():
    return get_settings()['TRADING']['lot']

def stop_loss():
    return get_settings()['TRADING']['stop_loss']

def symbol():
    return get_settings()['TRADING']['symbol']

def stop_loss():
    return get_settings()['TRADING']['stop_loss']

def max_ticks():
    return get_settings()['DATA']['max_ticks']

def account():
    login =  get_settings()['ACCOUNT']['login']
    password =  get_settings()['ACCOUNT']['password']
    server =  get_settings()['ACCOUNT']['server']

    return {
        'login': int(login),
        'password': password,
        'server': server,
    }
def start_year():
    return get_settings()['MODEL']['start_year']


