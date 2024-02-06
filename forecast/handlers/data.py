import pandas as pd
from ..params import ModelParams
import numpy as np
from dateutil.relativedelta import relativedelta

params = ModelParams()




# differencing to remove trend
def diff_data(df, diff_order=None, method=None):
    df.sort_index(ascending=True, inplace=True)
    if diff_order is None:
        diff_order = params.diff_order
    for column in df.columns:
        if method is None or method == 'pct_change':
            df[column] = df[column].pct_change(diff_order)
        elif method == 'log':
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




def undiff_data(df_predictions, df_data, diff_order=None):
    target_column = params.target_column
    diff_order = params.diff_order
    steps = params.steps
    if diff_order is None:
        diff_order = params.diff_order
    shift_len = diff_order - steps
    diff_1 = df_data.tail(shift_len + 1).head(1)[target_column].values[0]
    pred = df_predictions['prediction'].values[0]
    pred_undiff = np.exp(pred + np.log(diff_1))
    return pred_undiff
    # shifted_column = f'close_{diff_order}_hours_ago'
    # df_data[shifted_column] = df_data[target_column].shift(diff_order)
    # df_data[shifted_column] = np.log(df_data[shifted_column])
    # df_data['prediction'] = df_data[shifted_column] + df_predictions['prediction']
    # df_data['prediction'] = np.exp(df_data['prediction'] )
    # return df_data





## Rolling predictions
# def forecast_rolling(df_test, model_fit, lags=None, steps=None):
#     if lags is None:
#         lags = LAGS
#     if steps is None:
#         steps = STEPS
#     df_predictions = pd.DataFrame()
#     df_rolling = df_test.head(lags)
#     df_test = df_test.tail(-lags)
#     for i, row in df_test.iterrows():
#         df_test_next = row.to_frame().T
#         # model = VAR(df_rolling)
#         # model_fit = model.fit(maxlags=LAGS)
#         predictions = model_fit.forecast(steps=steps, y=df_rolling.tail(lags).values)
#         predictions = [predictions[-1]]
#         # #get the predictions and residuals
#         predictions = pd.DataFrame(data=predictions, index=[df_test_next.index[0] + relativedelta(hours=(steps-1)*4)], columns=df_test.columns.values)
#         if df_predictions.empty:
#             df_predictions = predictions
#         else:
#             df_predictions = pd.concat([df_predictions, predictions], axis=0)
        

        
#         df_rolling = pd.concat([df_rolling, df_test_next], axis=0)

    

    # df_residuals = df_test - df_predictions
    # df_predictions.rename(columns={TARGET_COLUMN: 'prediction'}, inplace=True)
    # model_fit.is_stable(verbose=False)
    # return df_predictions, df_residuals, df_test
