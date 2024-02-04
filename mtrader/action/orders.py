import MetaTrader5 as mt5
from utils.logs import logger

class OrderRequest():
    def __init__(self, 
                 action,
                 symbol,
                 volume,
                 type,
                 magic,
                 sl=None,
                 tp=None,
                 comment=None,
                 deviation=20,) -> None:
        if action == 'trade':
            self.action = mt5.TRADE_ACTION_DEAL
        else:
            self.action = action
        self.magic = magic
        self.symbol = symbol
        self.volume = volume
        self.type_str = type
        if type.lower() == "buy":
            self.type = mt5.ORDER_TYPE_BUY
        elif type.lower() == "sell":
            self.type = mt5.ORDER_TYPE_SELL
        # self.price,
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

        self._request = self.create_order()

    def create_order(self):
        price = mt5.symbol_info_tick(self.symbol).ask \
            if self.type_str.lower() == 'buy' \
            else mt5.symbol_info_tick(self.symbol).bid
        self._request = {
            'action': self.action,
            'symbol': self.symbol,
            'volume': self.volume,
            'type': self.type,
            'price': price,
            'sl': self.sl,
            'tp': self.tp,
            'deviation': self.deviation,
            'magic': self.magic,
            'comment': self.comment,
            'type_time': self.type_time,
            'type_filling': self.type_filling
        }

        return self._request
    
    def send_order(self):
        result = None
        active_orders_count = self.active_orders()
        if active_orders_count == 0:
            result = mt5.order_send(self._request)
            if result is None:
                logger.error(f"Could not open '{self.type_str.upper()}' trade {self.magic}. Unidentified reason.")
        else:
            logger.warning(f"Could not open '{self.type_str.upper()}' trade {self.magic}. There are {active_orders_count} at the moment. Try again later :)")
        
        return result
    
    def __str__(self) -> str:
        if self._request is not None:
            return self.magic
        return False


    def active_orders(self):
        positions_total = mt5.positions_total()
        return positions_total
            



