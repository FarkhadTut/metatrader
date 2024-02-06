
import MetaTrader5 as mt5
from mtrader.data.handler import load_data
from mtrader.action.orders import OrderRequest
from mtrader.account.connection import establish_connection
from forecast.prediction import get_predictions
import time
from config.settings import TradeConfig

config = TradeConfig()
order_live_hours = config.order_live_hours

if __name__ == '__main__':
    establish_connection()
    # get data on MetaTrader 5 version
    


    

    while True:
        df = load_data()
        prediction = get_predictions(df)
        order_request = OrderRequest(
            prediction=prediction
            )
        difference = prediction - order_request.price_open
        result = order_request.open_trade()
        if result:
            time.sleep(order_live_hours * 60 * 60)
            result = order_request.close_trade()
        else:
            time.sleep(3)

    # shut down connection to MetaTrader 5
    mt5.shutdown()
