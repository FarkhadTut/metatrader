import pandas as pd
import numpy as np
from dateutil.relativedelta import relativedelta
import datetime
from config.settings import TradeConfig
config = TradeConfig()

FILES = {
    'daily': 'EURUSD1440.csv',
    'hourly': 'EURUSD240.csv',
}

START_YEAR = 2015
END_YEAR = None

def read_data(path, start_year=None, end_year=None):
    df = pd.read_csv(f'test\\data\\{path}', header=None, sep='\t', skiprows=1)
    df.reset_index(inplace=True, drop=True)
    if len(df.columns) == 8:
        df['<TIME>'] = datetime.datetime.strptime('00:00', '%H:%M').time()
        df['<TIME>'] = '00:00'
        df.columns = ['date', 'open', 'high', 'low', 'close', 'tick_volume', 'volume', 'spread', 'time']
    else:
        df.columns = ['date', 'time', 'open', 'high', 'low', 'close', 'tick_volume', 'volume', 'spread']

    df['datetime'] = pd.to_datetime(df.index.map(lambda x: " ".join([str(df.loc[x, 'date']), str(df.loc[x, 'time'])])))

    df.set_index('datetime', inplace=True)
    if start_year is not None:
        df = df[df.index.year >= START_YEAR]
    if end_year is not None:
        df = df[df.index.year < end_year]

    df = df[['close', 'tick_volume']]
    df.rename(columns={'close': 'close_hourly'}, inplace=True)
    return df


# differencing to remove trend
def diff_data(df, diff_order=None, method=None):
    df.sort_index(ascending=True, inplace=True)
    if diff_order is None:
        diff_order = config.diff_order
    for column in df.columns:
        if method == 'pct_change':
            df[column] = df[column].pct_change(diff_order)
        elif method is None or method == 'log':
            df[column] = np.log(df[column]) - np.log(df[column].shift(diff_order))
    # df.dropna(how='any', axis=0, inplace=True)
    df = df.tail(-diff_order)
    return df



    
## removing seasonality
def remove_seasonality(df):
        df_month_mean = df.groupby(by=df.index.month).mean()
        df_month_mean.reset_index(drop=False, inplace=True)
        df_month_mean.rename(columns={'index': 'month'}, inplace=True)
        df['month'] = df.index.month
        df.reset_index(drop=False, inplace=True)
        # df['price_month_mean'] = df.index.map(lambda x: df_month_mean.loc[int(x.split('-')[1]), 'price_mean'])
        # print(df)
        df = pd.merge(df, df_month_mean, on=['month'], how='left', suffixes=('', '_mean'))
        price_columns = [c for c in df.columns if '_mean' not in c and 'room' in c]
        for c in price_columns:
            c_mean = c+'_mean'
            df[c] = df[c] - df[c_mean]
            df.drop(c_mean, axis=1, inplace=True)

        df.set_index('index', inplace=True)
        df.drop(['month'], axis=1, inplace=True)
        df.drop([c for c in df.columns if c.endswith('_mean')], axis=1, inplace=True)
        df.index = pd.to_datetime(df.index).tz_localize(None)
        return df


def forecast(model_fit, df_test):
    predictions = model_fit.forecast(steps=df_test.shape[0], y=df_test.values)
    df_predictions = pd.DataFrame(data=predictions, index=df_test.index, columns=df_test.columns.values)
    df_residuals = df_test - df_predictions
    return df_predictions, df_residuals




def undiff_data(df_predictions, df_data, target_col=None, diff_order=None):
    if diff_order is None:
        diff_order = config.diff_order
    if target_col is None:
        target_col = 'prediction'
    shifted_column = f'close_{diff_order}_hours_ago'
    df_data[shifted_column] = df_data[config.target_column].shift(diff_order)

    df_data[shifted_column] = np.log(df_data[shifted_column])
    df_data[target_col] = df_data[shifted_column] + df_predictions[target_col]
    df_data[target_col] = np.exp(df_data[target_col])
    df_data[shifted_column] = df_data[config.target_column].shift(diff_order)
    return df_data

def get_merged_data():
    df_hourly = read_data(FILES['hourly'], start_year=START_YEAR, end_year=END_YEAR)
    return df_hourly

def load_data():
    df = get_merged_data()
    split_point = int(df.shape[0]*config.train_size)
    df_train = df.head(split_point)
    df_test = df.tail(df.shape[0] - split_point)
    return df_train, df_test



## Rolling predictions
def forecast_rolling(df_test, model_fit, lags=None, steps=None):
    if lags is None:
        lags = config.lags
    if steps is None:
        steps = config.steps
    df_predictions = pd.DataFrame()
    df_rolling = df_test.head(lags)
    df_test = df_test.tail(-lags)
    for idx, row in df_test.iterrows():
        df_test_next = row.to_frame().T
        # model = VAR(df_rolling)
        # model_fit = model.fit(maxlags=config.lags)
        predictions = model_fit.forecast(steps=steps, y=df_rolling.tail(lags).values)
        target_pred = [predictions[-1]]

        ## get the predictions and residuals
        df_target_pred = pd.DataFrame(data=target_pred, 
                                   index=[idx + relativedelta(hours=(steps)*4)], 
                                   columns=df_test.columns.values)

        ## add the previous steps of the forecast to dataframe
    

        if df_predictions.empty:
            df_predictions = df_target_pred
        else:
            df_predictions = pd.concat([df_predictions, df_target_pred], axis=0)
        


        df_rolling = pd.concat([df_rolling, df_test_next], axis=0)


    df_predictions_test = pd.merge(df_predictions, df_test, how='inner', right_index=True, left_index=True, suffixes=('', '_test'))
    test_columns = [c for c in df_predictions_test.columns if '_test' in c]
    pred_columns = [c for c in df_predictions_test.columns if not '_test' in c]
    df_test = df_predictions_test[test_columns]
    df_test.columns = [c.replace('_test', '') for c in df_test.columns]
    df_predictions = df_predictions_test[pred_columns]
    df_residuals = df_predictions - df_test
    
    df_predictions.rename(columns={config.target_column: 'prediction'}, inplace=True)
    return df_predictions, df_residuals, df_test
