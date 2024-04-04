import pandas as pd
from mtrader.data.handler import load_data
from .handlers.data import (
    diff_data,
    undiff_data,
    mt_undiff_data,
)
from .model.deployed import predict
from .params import ModelParams
import datetime

params = ModelParams()




def get_predictions(df_data):
    df = diff_data(df_data.copy(), method='log')

    df_prediction = predict(df)

    # df_predict_merged = undiff_data(df_prediction.copy(), df_data.copy(), target_col='prediction')
    # prediction= df_predict_merged['prediction'].values[-1]


    prediction = mt_undiff_data(df_prediction.copy(), df_data.copy())
    

    return prediction




