
import MetaTrader5 as mt5
from database.connection import Database
from config.settings import TradeConfig
from datetime import datetime 
from utils.logs import logger
from utils.functions import minutes_between_datetimes
from dateutil.relativedelta import relativedelta


database = Database()
config = TradeConfig()

class MarketState():
    def __init__(self) -> None:
        self.trades = []
        self.orders = []

    def get_open_trades(self):
        self.trades = self.get_by_symbol()
        return self.trades 
    
    def get_wait_time(self):
        
        if len(self.orders) == 1:
            order = self.orders[0]
            open_time_str = order[3]
            open_time_str = open_time_str.split('.')[0]
            open_time = datetime.strptime(open_time_str, '%Y-%m-%d %H:%M:%S')
            order_live_hours = config.order_live_hours
            close_time = open_time + relativedelta(hours=order_live_hours)
            minutes = minutes_between_datetimes(datetime.now(), close_time)
            hours = round(minutes/60, 1)
            return minutes, hours
        
        logger.error("There is more than 1 open trades registered in database.")
            

    def count_open_orders(self):
        open_trades = self.get_open_trades()
        orders = []
        for trade in open_trades:
            position_id = trade.ticket
            order = database.get_order_by_pid(position_id)
            if order is not None:
                orders.append(order)

        self.orders = orders
        return len(orders)
    

    def open_orders_by_bot(self):
        open_trades = self.get_open_trades()
        orders = []
        for trade in open_trades:
            position_id = trade.ticket
            order = database.get_order_by_pid(position_id)
            if order is not None:
                orders.append(order)

        self.orders = orders
        return orders


    def get_by_pid(self, position_id):
        order = mt5.positions_get(
            ticket=position_id      
            )
        return order
    
    def get_by_symbol(self):
        trades = mt5.positions_get(
            symbol=config.symbol      
            )
        return trades
    
    def open_position_id(self):
        order = self.orders[0]
        position_id = order[1]
        return position_id
    
    def close_trade(self, position_id):
        while True:
            try:
                result = mt5.Close(
                    symbol=config.symbol, 
                    ticket=position_id
                    )
                if result == True:
                    break
                else:
                    raise Exception('Could not close order position_id={position_id}, result={result}')
            except Exception as e:
                logger.error(f'While closing order. {str(e)}')
    
        
            