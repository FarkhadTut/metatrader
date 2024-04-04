

from statsmodels.iolib.smpickle import load_pickle
import os
from ..params import ModelParams
import pandas as pd
import datetime
params = ModelParams()

def load_model():
    filename = 'VAR_eur_mape_1440v240_step=3_do=7_l=6_mape=66.002_2024-04-05.pkl'
    file_path = os.path.join(os.getcwd(), 'forecast', 'model', 'evolution', filename) 
    model = load_pickle(file_path)
    return model

model = load_model()


def predict(df):
    steps = params.steps
    lags = params.lags
    time_prediction = df.tail(1).index.values[0]
    predictions = model.forecast(steps=steps, y=df.tail(lags).values)
    # predictions, lower, upper = model.forecast_interval(y=df.tail(lags).values, steps=steps, alpha=0.05)
    predictions = [predictions[-1]]
    df_predictions = pd.DataFrame(data=predictions, 
                                  index=[time_prediction],
                                  columns=df.columns.values)
    
    
    df_predictions.rename(columns={params.target_column: 'prediction'}, 
                          inplace=True)
    
    # if pd.to_datetime(df.index.values[-1]).date() == datetime.date(2022,12,5):
    #     print(df.tail(lags))
    #     print(df_predictions)
    #     print('steps:',steps, 'lags:', lags)
    #     exit()

    return df_predictions
