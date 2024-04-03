
from statsmodels.tsa.api import VAR
# optional import, only use for demo
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
from test.data import load_data
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
        self.max_orders = 2
        self.orders = []

        df_train, df_test = load_data()
        df_train = diff_data(df_train.copy(), method='log')
        model = VAR(df_train)
        self.model_fit = model.fit(maxlags=config.lags, trend='n', ic='fpe')

    # for the last candle (data) of the given currency (symbol), provided its historical data(history) predict whether to buy or sell
    def predict(self, history):

        # convert history to pandas dataframe
        history_dataframe = pd.DataFrame(history, columns=("date", "open", "high", "low", "close", "tick_volume","pos"))
        history_dataframe.drop(columns=['close', 'high', 'low', 'pos'], inplace=True)
        history_dataframe.rename(columns={'open': 'close_hourly'}, inplace=True)
        history_dataframe.set_index('date', inplace=True)
        history_dataframe = history_dataframe.shift(freq='-4H')
        print(history_dataframe)
        exit()
        # history_dataframe = history_dataframe.head(-1)
        # history_dataframe['close_daily'] = history_dataframe[history_dataframe['close_daily'].index.hour == 20]['close_daily']
        
        # extract meaningful values
        curr_close_price = history[-1][4]
        date = history[-1][0]
        

        
        ###############################################
        # adjust TP/SL values here, remember to x100 if testing on JPY currency
        #take_profit = 0.0200
        take_profit = 0.050
        #stop_loss = -0.0250
        stop_loss = 0.050
        # print('Cur time:', date)
        

        prediction = get_predictions(history_dataframe, self.model_fit)
        curr_close_price = history_dataframe.tail(1).values[0][0]
        # print("-----")
        # print("date: ", date)
        # print("current price is: ", curr_close_price)

        
        if prediction >= curr_close_price:
            signal = 1
        elif prediction < curr_close_price:
            signal = -1

        # close_dict = {}
        # if len(self.orders) != 0:
        #     for order in self.orders[:]:
        #         date_order = order['date']
        #         diff_hours = int((date - date_order).total_seconds() / 3600)
        #         # print(f'DATES {date_order} -- {date}')
        #         if diff_hours >= config.steps * 4:
        #             # action_dict =  {"action":"skip"}
        #             close_dict = {"close_action":"POSITION_CLOSE_SYMBOL"}
        #             self.orders = [ord for ord in self.orders if not (ord['date'] == date_order)]
            # else:
            #     self.prev_trade_time = None
            #     action_dict = {"action":"POSITION_CLOSE_SYMBOL"}

            # return action_dict


        self.prev_trade_time = date

        if signal == 1:

            self.prev_signal = signal
            self.prev_traded_price = curr_close_price
            self.curr_stop_loss = curr_close_price - stop_loss
            self.curr_take_profit = curr_close_price + take_profit
            action_dict = {"action":"ORDER_TYPE_BUY", #buy
                    "takeprofit": curr_close_price + take_profit,
                    "stoploss": curr_close_price - stop_loss}

        if signal == -1:
            self.prev_signal = signal
            self.prev_traded_price = curr_close_price
            self.curr_stop_loss = curr_close_price + stop_loss
            self.curr_take_profit = curr_close_price - take_profit
            action_dict = {"action":"ORDER_TYPE_SELL", #sell
                    "takeprofit": curr_close_price - take_profit,
                    "stoploss": curr_close_price + stop_loss}

        self.orders.append({'date': date})
        # action_dict = action_dict | close_dict
        return action_dict
       


ai = DecisionMaker()
executor = actionWriter(ai)
executor.run()
