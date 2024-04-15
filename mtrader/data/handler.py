import MetaTrader5 as mt5
from datetime import datetime
import pandas as pd
from config.settings import (
    TradeConfig,
    )
from utils.functions import generate_time_list

KEEP_COLUMNS = ['date', 'close', 'tick_volume']

config = TradeConfig()


def imputation(df):
    start_datetime = df.index.values[0]
    end_datetime = df.index.values[-1]
    datetime_list = generate_time_list(start_datetime, end_datetime)
    df_new = pd.DataFrame(columns=df.columns, 
                 index=datetime_list)
    df_new = pd.merge(df_new, df, how='left', right_index=True, left_index=True, suffixes=('_nan', ''))
    drop_columns = [c for c in df_new.columns if '_nan' in c]
    df_new.drop(columns=drop_columns, inplace=True)
    df_new = df_new.interpolate()

    return df

def load_data():
    max_ticks = int(config.max_ticks)
    hourly_data = mt5.copy_rates_from("EURUSD_i", mt5.TIMEFRAME_H4, datetime.now(), max_ticks)
    # daily_data = mt5.copy_rates_from("EURUSD_i", mt5.TIMEFRAME_D1, datetime.now(), int(max_ticks/5))

    df_hourly = pd.DataFrame(hourly_data)
    # df_daily = pd.DataFrame(daily_data)

    df_hourly.rename(columns={'time': 'date'}, inplace=True)
    # df_daily.rename(columns={'time': 'date'}, inplace=True)

    df_hourly = df_hourly[KEEP_COLUMNS]
    # df_daily = df_daily[KEEP_COLUMNS]


    df_hourly['date']=pd.to_datetime(df_hourly['date'], unit='s')
    # df_daily['date']=pd.to_datetime(df_daily['date'], unit='s')
    # df = pd.merge(df_hourly, df_daily, on='date', how='left', suffixes=('_hourly', '_daily'))
    # df['close_daily'] = df['close_daily'].ffill()
    # df.dropna(how='any', axis=0, inplace=True)
    df = df_hourly.copy()
    df.rename(columns={'close': 'close_hourly'}, inplace=True)
    df.set_index('date', drop=True, inplace=True)
    df = df[df.index.year >= int(config.start_year)]
    # df['close_daily'] = df['close_daily'].shift(6)
    df.dropna(axis=0, how='any', inplace=True)
    # df = df.shift(freq='4H')
    df = imputation(df.copy())
    return df

def imputation(df):
    start_datetime = df.index.values[0]
    end_datetime = df.index.values[-1]
    datetime_list = generate_time_list(start_datetime, end_datetime)
    df_new = pd.DataFrame(columns=df.columns, 
                 index=datetime_list)
    df_new = pd.merge(df_new, df, how='left', right_index=True, left_index=True, suffixes=('_nan', ''))
    drop_columns = [c for c in df_new.columns if '_nan' in c]
    df_new.drop(columns=drop_columns, inplace=True)
    df_new = df_new.interpolate()
   
    return df_new
