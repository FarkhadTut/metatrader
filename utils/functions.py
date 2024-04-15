
from datetime import datetime
from dateutil.relativedelta import relativedelta
import pandas as pd
import numpy as np
from config.settings import TradeConfig

config = TradeConfig()

def minutes_between_datetimes(start_datetime, end_datetime):
    # Calculate the difference between the datetimes
    time_difference = end_datetime - start_datetime
    
    # Convert the difference to minutes
    minutes = time_difference.total_seconds() / 60
    
    return int(minutes)


def generate_time_list(start_datetime, end_datetime):
    """
    Generates a list of datetime objects with 4-hour intervals, excluding weekends.

    Args:
        start_datetime: The starting datetime object.
        end_datetime: The ending datetime object.

    Returns:
        A list of datetime objects within the specified range, excluding weekends.
    """
    start_datetime = pd.to_datetime(start_datetime)
    end_datetime = pd.to_datetime(end_datetime)
    time_list = []
    current_time = start_datetime
    while current_time <= end_datetime:
        if current_time.dayofweek not in (5, 6):  # Skip Saturdays and Sundays (weekend days)
            time_list.append(current_time)
        current_time += relativedelta(hours=4)
    return time_list


def calculate_profit(df_data, steps=None):
    # df_data['result_p'] = (df_data['prediction'].shift(-STEPS) - df_data['close_hourly']) * LEVERAGE * LOT * 100
    # df_data['result'] = (df_data['close_hourly'].shift(-STEPS) - df_data['close_hourly']) * LEVERAGE * LOT * 100
    # profit without stop loss
    # df_data['profit'] = df_data.index.map(lambda x: -1* abs(df_data.loc[x, 'result'])\
    #                                                 if ((df_data.loc[x, 'result'] > 0 and df_data.loc[x, 'result_p'] <=0) \
    #                                                 or (df_data.loc[x, 'result'] <= 0 and df_data.loc[x, 'result_p'] >= 0))
    #                                                 else abs(df_data.loc[x, 'result']))
    #####################
    if steps is None:
        steps = config.steps

    LEVERAGE = 500
    LOT = 1
    target_column = 'close_hourly'
    df_data['profit'] = np.nan
    compare_col = target_column + f'_{steps}_steps_ago'
    df_data[compare_col] = df_data[target_column].shift(steps)
    df_data['prediction'] = df_data['prediction'].shift(steps)
    for x in df_data.index:
        if (df_data.loc[x, compare_col] >= df_data.loc[x, target_column] and df_data.loc[x, compare_col] >= df_data.loc[x, 'prediction']) \
             or (df_data.loc[x, compare_col] <= df_data.loc[x, target_column] and df_data.loc[x, compare_col] <= df_data.loc[x, 'prediction']):
            
            df_data.loc[x, 'profit'] = abs(df_data.loc[x, target_column] - df_data.loc[x, compare_col])* LEVERAGE * LOT * 100
        else:
            df_data.loc[x, 'profit'] = -abs(df_data.loc[x, target_column] - df_data.loc[x, compare_col])* LEVERAGE * LOT * 100

    
    # profit with stop loss
    
    # df_data['max_price'] = df_data['close_hourly'].rolling(window=STEPS).max()
    # df_data['min_price'] = df_data['close_hourly'].rolling(window=STEPS).min()
    # print(df_data)
    # print()
    # exit()
    

    

    return df_data