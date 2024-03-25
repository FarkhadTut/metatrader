

from statsmodels.iolib.smpickle import load_pickle
import os
from ..params import ModelParams
import pandas as pd
from dateutil.relativedelta import relativedelta

params = ModelParams()

def load_model():
    filename = 'VAR_eur_mape_1440v240_step=4_do=5_l=9_mape=49.0364_2024-03-24.pkl'
    file_path = os.path.join(os.getcwd(), 'forecast', 'model', 'evolution', filename) 
    model = load_pickle(file_path)
    return model

model = load_model()


def predict(df):
    steps = params.steps
    lags = params.lags

    predictions = model.forecast(y=df.tail(lags).values, steps=steps)
    predictions = [predictions[-1]]
    df_predictions = pd.DataFrame(data=predictions, 
                                  index=[df.index[-1] + relativedelta(hours=steps*4)],
                                  columns=df.columns.values)
    
    df_predictions.rename(columns={params.target_column: 'prediction'}, 
                          inplace=True)
    
   
    return df_predictions
