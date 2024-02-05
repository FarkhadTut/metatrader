import MetaTrader5 as mt5
from utils.logs import logger
from typing import Dict
from config.settings import TradeConfig
from database.connection import database

config = TradeConfig()


class OrderRequest():
    def __init__(self, 
                 action,
                 type,
                 magic,
                 sl=None,
                 tp=None,
                 comment=None,) -> Dict:
        
        symbol = config.symbol
        lot = config.lot
        deviation = config.deviation

        if action == 'trade':
            self.action = mt5.TRADE_ACTION_DEAL
        else:
            self.action = action
        self.magic = magic
        self.symbol = symbol
        self.volume = lot
        self.type_str = type
        if type.lower() == "buy":
            self.type = mt5.ORDER_TYPE_BUY
        elif type.lower() == "sell":
            self.type = mt5.ORDER_TYPE_SELL
        self.sl = sl
        self.tp = tp
        self.deviation = deviation
        self.comment = comment
        self.type_time = mt5.ORDER_TIME_GTC
        self.type_filling = mt5.ORDER_FILLING_RETURN
        symbol_info = mt5.symbol_info(symbol)
        if symbol_info is None:
            print(symbol, "not found, can not call order_check()")
            mt5.shutdown()
            exit()
        self.point = symbol_info.point
        

        self.create_order()
        

    def create_order(self):
        price = mt5.symbol_info_tick(self.symbol).ask \
            if self.type_str.lower() == 'buy' \
            else mt5.symbol_info_tick(self.symbol).bid

        self._request = {
            "action": self.action,
            "symbol": self.symbol,
            "volume": self.volume,
            "type": self.type,
            "price": price,
            "sl": price - 100 * self.point,
            "tp": price + 100 * self.point,
            "deviation": self.deviation,
            "magic": 234000,
            "comment": "python script open",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_RETURN,
        }
    

    def save_order(self, retcode):
        if retcode != mt5.TRADE_RETCODE_DONE:
            return False
        else:
            database.save_order(self._request)
            return True

    def send_order(self):
        result = None
        active_orders_count = self.active_orders()
        if active_orders_count == 0:
            result = mt5.order_send(self._request)
            if result is None:
                logger.error(f"Could not open '{self.type_str.upper()}' trade {self.magic}. Return code: {result.retcode}")
        else:
            logger.warning(f"Could not open '{self.type_str.upper()}' trade {self.magic}. There are {active_orders_count} at the moment. Try again later :)")

        
        self.save_order(result.retcode)
        return result
    
    def __str__(self) -> str:
        if self._request is not None:
            return f'<Order {self.type_str.upper()}:{str(self.magic)}>'
        return False


    def active_orders(self):
        positions_total = mt5.positions_total()
        return positions_total
            



