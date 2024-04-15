
import MetaTrader5 as mt5
from mtrader.data.handler import load_data
from mtrader.action.orders import OrderRequest
from mtrader.account.connection import establish_connection
from mtrader.state.trades import MarketState
from forecast.prediction import get_predictions
import time
from config.settings import TradeConfig
from utils.logs import logger
from utils.functions import minutes_between_datetimes
from dateutil.relativedelta import relativedelta
from datetime import datetime

config = TradeConfig()
market_state = MarketState()
order_live_hours = config.order_live_hours

if __name__ == '__main__':
    establish_connection()
    # get data on MetaTrader 5 version
    
    next_trade_time = None
    open_trades = []
    while True:
        open_trades_count = market_state.count_open_orders()
        df = load_data()
        cur_trade_time = df.index[-1]
        # next_trade_time = cur_trade_time + relativedelta(hours=4)
        # time_now = datetime.now()
        prediction = get_predictions(df)
        order_request = OrderRequest(
            prediction=prediction
            )
        if open_trades_count == 0:
            prediction = get_predictions(df)
            order_request = OrderRequest(
                prediction=prediction
                )
            result = order_request.open_trade()
            if result:
                open_trades.append((order_request, cur_trade_time))

                
        elif open_trades_count <= config.max_orders:
            if cur_trade_time not in list(set([t[1] for t in open_trades])):
                prediction = get_predictions(df)
                order_request = OrderRequest(
                    prediction=prediction
                    )
                result = order_request.open_trade()
                if result:
                    open_trades.append((order_request, cur_trade_time))
                

      

        for open_order in market_state.open_orders_by_bot():
            position_id = int(open_order[1])
            _type = 'SELL' if int(open_order[8]) == 1 else 'BUY'
            time_open = open_order[3].split('.')[0]
            time_open = datetime.strptime(time_open, '%Y-%m-%d %H:%M:%S')
            time_now = datetime.now()
            hours_passed = minutes_between_datetimes(time_open, time_now)/60
            hours_passed = round(hours_passed, 1)
            logger.info(f"OrderID {position_id} ({_type}): {hours_passed} hours passed.")
            if hours_passed >= 12:
                market_state.close_trade(position_id)
        
            ### not finished. check all open trades' time and print how long left and close if expired
            # logger.error(f'There are {open_trades_count} trades going on.')
            # position_id = market_state.open_position_id()
            # wait_minutes, wait_hours = market_state.get_wait_time()
            # logger.info(f"There is an unclosed order in database. Time to wait (h): {wait_hours}")
            # prediction = get_predictions(df)
            # order_request = OrderRequest(
            #     prediction=prediction
            #     )
            # print(order_request)
            # time.sleep(wait_minutes * 60)
            # market_state.close_trade(position_id)



        time.sleep(30)

    # shut down connection to MetaTrader 5
    mt5.shutdown()
