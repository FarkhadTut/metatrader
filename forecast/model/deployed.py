

from statsmodels.iolib.smpickle import load_pickle
import os
from ..params import ModelParams
import pandas as pd
from dateutil.relativedelta import relativedelta

params = ModelParams()

def load_model():
    filename = 'VAR_eur_mape_1440v240_step=3_do=3_l=9_mape=105.999_2024-04-02.pkl'
    file_path = os.path.join(os.getcwd(), 'forecast', 'model', 'evolution', filename) 
    model = load_pickle(file_path)
    return model

model = load_model()


def predict(df):
    steps = params.steps
    lags = params.lags
    time_prediction = df.tail(params.steps).index.values
    predictions = model.forecast(y=df.tail(lags).values, steps=steps)
    # predictions, lower, upper = model.forecast_interval(y=df.tail(lags).values, steps=steps, alpha=0.05)
    # predictions = [predictions[-1]]
    df_predictions = pd.DataFrame(data=predictions, 
                                  index=time_prediction,
                                  columns=df.columns.values)
    
    df_predictions.rename(columns={params.target_column: 'prediction'}, 
                          inplace=True)

    return df_predictions
