
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
        stop_loss = -0.050
        # print('Cur time:', date)
        

        prediction = get_predictions(history_dataframe)

        # print("-----")
        # print("date: ", date)
        # print("current price is: ", curr_close_price)

        
        if prediction > curr_close_price:
            signal = 1
        elif prediction < curr_close_price:
            signal = -1
        else:
            signal = 0

        
        order = TestOrderRequest(prediction=prediction,
                                cur_price=curr_close_price,
                                time_open=date)
        
        position_id = database.save_open(order.open_request, test=True)


        if self.prev_trade_time is not None:
            diff_hours = int((date - self.prev_trade_time).total_seconds() / 3600)
            

            if diff_hours < config.steps * 4:
                return {"action":"skip"}, 0, self.prev_signal , df
            else:
                self.prev_trade_time = None
                self.prev_signal = 0
                return {"action":"POSITION_CLOSE_SYMBOL"} , signal, self.prev_signal, df #close
        else:  
            self.prev_trade_time = date


        print("prev trade time:", self.prev_trade_time)

        
        # first check if stop loss/take profit has been triggered
        if self.prev_signal == 1 and ((self.curr_take_profit != 0 and curr_high_price >= self.curr_take_profit) or (self.curr_stop_loss != 0 and curr_low_price <= self.curr_stop_loss)):
            self.prev_signal = 0 # since the sl/tp was triggered, we reset position

        if self.prev_signal == -1 and ((self.curr_take_profit != 0 and curr_low_price <= self.curr_take_profit) or (self.curr_stop_loss != 0 and curr_high_price >= self.curr_stop_loss)):
            self.prev_signal = 0 # since the sl/tp was triggered, we reset position
        
        # print("signal: ",signal)
        # print("prev_signal: ",self.prev_signal)
        # then we look at the signal returned
        if signal == 1:

            # if previous signal was a sell, close off the position
            # if self.prev_signal == -1:
            #     self.prev_signal = 0 # make previous signal 0 as we don't have an active position
            #     return {"action":"POSITION_CLOSE_SYMBOL"} , signal, self.prev_signal, df #close

            # if previous signal was 0, there was no active position, open a long position
            if self.prev_signal == 0:
                self.prev_signal = signal
                self.prev_traded_price = curr_close_price
                self.curr_stop_loss = curr_close_price + stop_loss
                self.curr_take_profit = curr_close_price + take_profit
                return {"action":"ORDER_TYPE_BUY", #buy
                        "takeprofit": curr_close_price + take_profit,
                        "stoploss": curr_close_price + stop_loss}, signal, self.prev_signal, df

            # otherwise, the previous signal was another buy (pre_signal == 1)
            # as a result, we do not buy again, instead we adjust the SL/TP
            else:
                self.prev_signal = signal 

                #if its a higher buy signal we increase our TP/SL by the same spread as the original
                if curr_close_price > prev_close_price and curr_close_price > self.prev_traded_price:
                    self.curr_stop_loss = curr_close_price + stop_loss
                    self.curr_take_profit = curr_close_price + take_profit
                    return {"action":"POSITION_MODIFY",
                            "takeprofit": curr_close_price + take_profit,
                            "stoploss": curr_close_price + stop_loss}, signal, self.prev_signal , df

                #if its a lower buy signal we dont change our take profit or stop loss
                else:
                    return {"action":"skip"}, signal, self.prev_signal , df

        if signal == -1:

            # # if previous signal was a buy, close off the position
            # if self.prev_signal == 1:
            #     self.prev_signal = 0 # make previous signal 0 as we don't have an active position
            #     return {"action":"POSITION_CLOSE_SYMBOL"} , signal, self.prev_signal, df #close

            # if previous signal was 0, there was no active position, open a short position
            if self.prev_signal == 0:
                self.prev_signal = signal
                self.prev_traded_price = curr_close_price
                self.curr_stop_loss = curr_close_price - stop_loss
                self.curr_take_profit = curr_close_price - take_profit
                return {"action":"ORDER_TYPE_SELL", #sell
                        "takeprofit": curr_close_price - take_profit,
                        "stoploss": curr_close_price - stop_loss}, signal, self.prev_signal , df

            # otherwise, the previous signal was another sell
            # as a result, we do not sell again, instead we adjust the SL/TP
            else:
                #if its a lower sell signal we increase our take profit and increase our stop loss by the same spread as the original
                if curr_close_price < prev_close_price and curr_close_price < self.prev_traded_price:
                    self.curr_stop_loss = curr_close_price - stop_loss
                    self.curr_take_profit = curr_close_price - take_profit
                    return {"action":"POSITION_MODIFY",
                            "takeprofit": curr_close_price - take_profit,
                            "stoploss": curr_close_price - stop_loss}, signal, self.prev_signal , df

                #if its a lower sell signal we dont change our take profit or stop loss aka do nothing
                else:
                    return {"action":"skip"}, signal, self.prev_signal , df

        if signal == 0:
            return {"action":"skip"}, signal, self.prev_signal , df


ai = DecisionMaker()
executor = actionWriter(ai)
executor.run()
