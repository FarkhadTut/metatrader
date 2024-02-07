
import MetaTrader5 as mt5
from mtrader.data.handler import load_data
from mtrader.action.orders import OrderRequest
from mtrader.account.connection import establish_connection
from mtrader.state.trades import MarketState
from forecast.prediction import get_predictions
import time
from config.settings import TradeConfig
from utils.logs import logger


config = TradeConfig()
market_state = MarketState()
order_live_hours = config.order_live_hours

if __name__ == '__main__':
    establish_connection()
    # get data on MetaTrader 5 version
    

    while True:
        open_trades_count = market_state.count_open_orders()
        if open_trades_count == 0:
            df = load_data()
            prediction = get_predictions(df)
            order_request = OrderRequest(
                prediction=prediction
                )
            result = order_request.open_trade()
            # if result:
            #     time.sleep(order_live_hours * 60 * 60)
            #     result = order_request.close_trade()
                
        elif open_trades_count == 1:
            position_id = market_state.open_position_id()
            wait_minutes, wait_hours = market_state.get_wait_time()
            logger.info(f"There is an unclosed order in database. Time to wait (h): {wait_hours}")
            time.sleep(wait_minutes * 60)
            market_state.close_trade(position_id)


        else:
            logger.error(f'There are {open_trades_count} trades going on.')

            

        time.sleep(3)

    # shut down connection to MetaTrader 5
    mt5.shutdown()
