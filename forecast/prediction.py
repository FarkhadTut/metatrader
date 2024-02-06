import pandas as pd
from mtrader.data.handler import load_data
from .handlers.data import (
    diff_data,
    undiff_data,
)
from .model.deployed import predict





def get_predictions(df_data):
    df = diff_data(df_data.copy(), method='log')
    df_prediction = predict(df)

    prediction = undiff_data(df_prediction, df_data.copy())
    return prediction




