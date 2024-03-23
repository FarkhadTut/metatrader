import MetaTrader5 as mt5
from utils.logs import logger
from typing import Dict
from config.settings import TradeConfig
from database.connection import database
import time
import random

config = TradeConfig()


class OrderRequest():
    def __init__(self, 
                 prediction,
                 sl=None,
                 tp=None,
                 comment=None,) -> Dict:
        
        self.prediction = prediction
        symbol = config.symbol
        lot = config.lot
        deviation = config.deviation
        self.action = mt5.TRADE_ACTION_DEAL
        self.magic = self.generate_unique_magic()
        self.symbol = symbol
        self.volume = lot
        self.sl = config.stop_loss
        self.tp = 50000
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
        self.position_id = None
        self.is_open = False
        self.price_open = None
        self.price_close = None
        self.type_str = None
        self.type = None

        self.create_open_request()
        
    def generate_unique_magic(self):
        while True:
            new_magic = random.randint(100000, 999999)
            if not database.magic_exists(new_magic):
                return new_magic

    def create_open_request(self):
        
        mean_price = (mt5.symbol_info_tick(self.symbol).ask + mt5.symbol_info_tick(self.symbol).bid) / 2
        price_diff =  self.prediction - mean_price
        if price_diff < 0:
            self.type = mt5.ORDER_TYPE_SELL
            self.type_str = 'sell'
            price = mt5.symbol_info_tick(self.symbol).bid
            stop_loss = price + self.sl * self.point
            take_profit = price - self.tp * self.point
        elif price_diff > 0: 
            self.type = mt5.ORDER_TYPE_BUY
            self.type_str = 'buy'
            price = mt5.symbol_info_tick(self.symbol).ask
            stop_loss = price - self.sl * self.point
            take_profit = price + self.tp * self.point

        else:
            logger.error('Please write some logice for when predicted price is equal to current price.')
            exit()


        self.price_open = price
        self._request = {
            "action": self.action,
            "symbol": self.symbol,
            "volume": self.volume,
            "type": self.type,
            "price": price,
            "sl": stop_loss,
            "tp": take_profit,
            "deviation": self.deviation,
            "magic": 234000,
            "comment": "python script open",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_RETURN,
        }



    def save_open(self):
        self._request['point'] = self.point
        database.save_open(self._request)
        return True

    def save_close(self):
        result = database.save_close(self.position_id, self.price_close)
        return result

    def open_sucess(self, result):
        if result.retcode == mt5.TRADE_RETCODE_DONE:
            return True
        return False

    def open_trade(self):
        result = self.send_order()
        if result is not None and self.open_sucess(result):
            self._request['position_id'] = self.position_id
            return self.save_open()
        else:
            return False
        
    def close_trade(self):
        while True:
            try:
                result = mt5.Close(
                    self.symbol, 
                    ticket=self.position_id
                    )
                if result == True:
                    break
                else:
                    raise Exception(f'Could not close order position_id={self.position_id}, result={result}')
            except Exception as e:
                logger.error(f'While closing order. {str(e)}')
        self.is_open = not result

        if result:
            logger.info(f"Closed trade position_id={self.position_id}.")
            if self.type_str == 'buy':
                self.price_close = mt5.symbol_info_tick(self.symbol).bid
            else:
                self.price_close = mt5.symbol_info_tick(self.symbol).ask

            save_result = self.save_close()
            return save_result
        else:
            logger.error(f'Could not close order with position_id={self.position_id}.')
            return False

    def send_order(self):
        # active_orders_count = self.active_orders()
        
        while True:
            result = mt5.order_send(self._request)
            if self.open_sucess(result):
                self.position_id = result.order
                logger.debug(f"Opened '{self.type_str.upper()}' trade position_id={self.position_id}.")
                break
            elif result.retcode == mt5.TRADE_RETCODE_PRICE_OFF: ## not successful
                logger.error(f"Could not open '{self.type_str.upper()}' trade position_id={self.position_id}. Off quotes. Trying again...")
                time.sleep(1)
            elif result is None:
                logger.error(f"Could not open '{self.type_str.upper()}' trade position_id={self.position_id}. Unidentified reason, order_send return a None value.")
                return 
            else:
                logger.error(f"Could not open '{self.type_str.upper()}' trade position_id={self.position_id}. Returned {result.retcode}.")
                break

        return result
    
    def __str__(self) -> str:
        if self._request is not None:
            return f'<Order {self.type_str.upper()}:{str(self.magic)}>'
        return False


    def active_orders(self):
        positions_total = mt5.positions_total()
        return positions_total
            



