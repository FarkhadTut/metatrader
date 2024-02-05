
import MetaTrader5 as mt5
from utils.logs import logger
from config.settings import TradeConfig

config = TradeConfig()

# connect to MetaTrader 5
class Connector():
    def __init__(self,
                 login,
                 password,
                 server,
                 timeout=60,
                 portable=False
                 ) -> None:
        
        self.login = login
        self.password = password
        self.server = server
        self.timeout = timeout
        self.portable = portable
    
    def connect(self):
        initializer = mt5.initialize(
            login=self.login,
            password=self.password,
            server=self.server,
            timeout=self.timeout,
            portable=self.portable,
        )
        if initializer is None:
            print("initialize() failed")
            print(initializer)
            mt5.shutdown()
            exit()



def establish_connection():
    connector = Connector(**config.account)
    connector.connect()
    if mt5.terminal_info().connected:
        logger.debug(f"Connected to MetaTrader5.")
    else:
        logger.debug(f"Connected to MetaTrader5.")

            