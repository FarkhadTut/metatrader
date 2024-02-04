import MetaTrader5 as mt5
from datetime import datetime
import pandas as pd
from config.settings import (
    start_year,
    )
KEEP_COLUMNS = ['date', 'close']

def load_data(num_ticks):
    num_ticks = int(num_ticks)
    hourly_data = mt5.copy_rates_from("EURUSD_i", mt5.TIMEFRAME_H4, datetime.now(), num_ticks)
    daily_data = mt5.copy_rates_from("EURUSD_i", mt5.TIMEFRAME_D1, datetime.now(), int(num_ticks/5))

    df_hourly = pd.DataFrame(hourly_data)
    df_daily = pd.DataFrame(daily_data)

    df_hourly.rename(columns={'time': 'date'}, inplace=True)
    df_daily.rename(columns={'time': 'date'}, inplace=True)

    df_hourly = df_hourly[KEEP_COLUMNS]
    df_daily = df_daily[KEEP_COLUMNS]


    df_hourly['date']=pd.to_datetime(df_hourly['date'], unit='s')
    df_daily['date']=pd.to_datetime(df_daily['date'], unit='s')
    df = pd.merge(df_hourly, df_daily, on='date', how='left', suffixes=('_hourly', '_daily'))
    df['close_daily'] = df['close_daily'].ffill()
    df.dropna(how='any', axis=0, inplace=True)
    df.set_index('date', drop=True, inplace=True)
    df = df[df.index.year >= int(start_year())]
    return df