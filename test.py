
from test.trading_strategies.sma_ema import SimpleMAExponentialMA
# optional import, only use for demo
from datetime import datetime
#using pip install panda if missing modules pandas
import pandas as pd
# non-optional import:
from test.actionWriter import actionWriter
from forecast.prediction import get_predictions
from mtrader.action.orders import OrderRequest
from forecast.handlers.data import (
    diff_data,
    undiff_data,
)
from test.orders import TestOrderRequest
import sys
from config.settings import TradeConfig
from database.connection import Database

database = Database()
config = TradeConfig()

class DecisionMaker:

    def __init__(self):
        self.prev_signal = 0 # what the previous signal was was e.g. 1 for buy , -1 for sell, 0 for hold
        self.prev_traded_price = 0 # this is the previously traded price for an exisiting position (entry price)
        self.curr_stop_loss = 0 # current stop loss
        self.curr_take_profit = 0 # current take profit
        self.prev_trade_time = None # previous open trade time
        self.curr_trade_time = None # current open trade time

    # for the last candle (data) of the given currency (symbol), provided its historical data(history) predict whether to buy or sell
    def predict(self, history):

        # convert history to pandas dataframe
        history_dataframe = pd.DataFrame(history, columns=("date", "open", "high", "low", "close", "tick_volume","pos"))
        history_dataframe.drop(columns=['open', 'high', 'low', 'pos'], inplace=True)
        history_dataframe.rename(columns={'close': 'close_hourly'}, inplace=True)
        history_dataframe.set_index('date', inplace=True)
        history_dataframe = history_dataframe.shift(freq='4H')
        # history_dataframe = history_dataframe.head(-1)
        # history_dataframe['close_daily'] = history_dataframe[history_dataframe['close_daily'].index.hour == 20]['close_daily']
        
        # extract meaningful values
        prev_close_price = history[-2][4]
        curr_close_price = history[-1][4]
        curr_high_price = history[-1][2]
        curr_low_price = history[-1][3]
        date = history[-1][0]
        # Run strategy here ###########################
        strategy = SimpleMAExponentialMA(history)
        

        signal_lst, df = strategy.run_sma_ema()
        
        # signal = signal_lst[0]

        ###############################################
        # adjust TP/SL values here, remember to x100 if testing on JPY currency
        #take_profit = 0.0200
        take_profit = 0.050
        #stop_loss = -0.0250
        stop_loss = 0.050
        # print('Cur time:', date)
        

        prediction = get_predictions(history_dataframe)
        curr_close_price = history_dataframe.tail(1).values[0][0]
        # print("-----")
        # print("date: ", date)
        # print("current price is: ", curr_close_price)

        
        if prediction >= curr_close_price:
            signal = 1
        elif prediction < curr_close_price:
            signal = -1



        if self.prev_trade_time is not None:
            diff_hours = int((date - self.prev_trade_time).total_seconds() / 3600)
            if diff_hours < config.steps * 4:
                return {"action":"skip"}, signal, self.prev_signal , df
            else:
                self.prev_trade_time = None
                return {"action":"POSITION_CLOSE_SYMBOL"} , signal, self.prev_signal, df #close
            


        self.prev_trade_time = date

        if signal == 1:

            self.prev_signal = signal
            self.prev_traded_price = curr_close_price
            self.curr_stop_loss = curr_close_price - stop_loss
            self.curr_take_profit = curr_close_price + take_profit
            return {"action":"ORDER_TYPE_BUY", #buy
                    "takeprofit": curr_close_price + take_profit,
                    "stoploss": curr_close_price - stop_loss}, signal, self.prev_signal, df

        if signal == -1:
            self.prev_signal = signal
            self.prev_traded_price = curr_close_price
            self.curr_stop_loss = curr_close_price + stop_loss
            self.curr_take_profit = curr_close_price - take_profit
            return {"action":"ORDER_TYPE_SELL", #sell
                    "takeprofit": curr_close_price - take_profit,
                    "stoploss": curr_close_price + stop_loss}, signal, self.prev_signal, df

       


ai = DecisionMaker()
executor = actionWriter(ai)
executor.run()
