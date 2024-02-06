import pandas as pd
from scipy.stats.mstats import winsorize
import numpy as np


def date_parser(_date):
    return pd.to_datetime(_date).date


def normalize_data(df, columns=[]):
    if columns == 'all':
        columns = df.columns
    for c in columns:
        df[c]=(df[c]-df[c].mean())/df[c].std()
    return df


def clip_data(df, limits, _winsorize=False, columns=[]):
    if columns == 'all':
        columns = df.columns
    for c in columns:
        if _winsorize:
            df[c] = winsorize(df[c], limits=limits)
        else:
            df[c] = df[c].clip(upper=limits[0], lower=limits[1])
    return df

### Evaluation 
# def evaluate(df_residuals, df_data, verbose=False):
#     mape = (df_residuals[TARGET_COLUMN]/df_data[TARGET_COLUMN]) \
#                     .replace([np.inf, -np.inf], np.nan)\
#                     .dropna() \
#                     .mean()

#     mape = round(abs(mape)*100, 4)
#     rmse = np.sqrt(df_residuals[TARGET_COLUMN] \
#             .replace([np.inf, -np.inf], np.nan)\
#             .dropna() \
#             .pow(2) \
#             .mean())
#     rmse = round(abs(rmse)*100, 4)
    
#     if verbose:
#         print(f'Mean Absolute Percent Error: {mape}')
#         print(f'Root Mean Squared Error: {rmse}')
    
#     return mape, rmse


