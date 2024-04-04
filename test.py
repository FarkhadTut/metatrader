
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
from test.data import imputation
import datetime

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

        self.df_data = pd.DataFrame(columns=['datetime','close_hourly','tick_volume', 'prediction'])
        # self.df_predictions = pd.read_excel('test\\predictions\\df_predictions.xlsx')
        # self.df_predictions.set_index('datetime', inplace=True)
        # self.df_predictions = self.df_predictions.shift(-config.steps)


    # for the last candle (data) of the given currency (symbol), provided its historical data(history) predict whether to buy or sell
    def predict(self, history):

        # convert history to pandas dataframe
        history_dataframe = pd.DataFrame(history, columns=("date", "open", "high", "low", "close", "tick_volume","pos"))
        history_dataframe.drop(columns=['close', 'high', 'low', 'pos'], inplace=True)
        history_dataframe.rename(columns={'open': 'close_hourly'}, inplace=True)
        history_dataframe.set_index('date', inplace=True)
        history_dataframe = imputation(history_dataframe)
        # history_dataframe = history_dataframe.shift(freq='-4H')
        
        # history_dataframe = history_dataframe.head(-1)
        # history_dataframe['close_daily'] = history_dataframe[history_dataframe['close_daily'].index.hour == 20]['close_daily']
        
        # extract meaningful values
        # curr_close_price = history[-1][4]
        # curr_tick_volume = history[-1][5]

        curr_close_price = history_dataframe.tail(1)['close_hourly'].values[0]
        curr_tick_volume = history_dataframe.tail(1)['tick_volume'].values[0]
        date = history[-1][0]
        

        
        ###############################################
        # adjust TP/SL values here, remember to x100 if testing on JPY currency
        #take_profit = 0.0200
        take_profit = 0.050
        #stop_loss = -0.0250
        stop_loss = 0.050
        # print('Cur time:', date)
        

        prediction = get_predictions(history_dataframe)
        df_current = pd.DataFrame(columns=['datetime','close_hourly', 'tick_volume', 'prediction'],
                                    data=[[date, curr_close_price, curr_tick_volume, prediction]])
        self.df_data = df_current if self.df_data.empty else pd.concat([self.df_data, df_current], axis=0)
        self.df_data['datetime'] = pd.to_datetime(self.df_data['datetime'])
        self.df_data.reset_index(drop=True, inplace=True)
        # self.df_data.set_index('datetime', inplace=True)
        self.df_data.to_excel('test\\predictions\\df_data_test.xlsx')          
        curr_close_price = history_dataframe.tail(1).values[0][0]

        if pd.to_datetime(date).date() < datetime.date(2022,12,1):
            return {'action': 'skip'}

        ######## take prdictions from file ##########################################
        # if date in self.df_predictions.index:
        #     prediction = self.df_predictions.shift(-config.steps).loc[date, 'prediction']
        # else:
        #     return {'action': 'skip'}
        # if pd.isna(prediction):
        #     return {'action': 'skip'}
        ########################################################################
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

        elif signal == -1:
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
