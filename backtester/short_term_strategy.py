"""
File defining the short term strategy.
"""


import numpy as np
import pandas as pd
from scipy.signal import argrelextrema

from .api_downloader import get_data
from .strategy import Strategy
from .utils import Portfolio, TradingData, get_symbols_from_index


class ShortTermStrategy(Strategy):
    def __init__(self, data: TradingData, portfolio: Portfolio = None, *args, **kwargs):
        super().__init__(data, portfolio)
        self.riskmetric = self.compute_metric()
        print(self.portfolio)
        self.buy()
        print(self.portfolio)

    def compute_metric(self):
        args = {
            "ticker": next(iter(get_symbols_from_index(self.data))),
            "start_date": pd.Timestamp("2017-01-01"),
            "end_date": pd.Timestamp("2022-05-01"),
            "interval": "5m",
        }
        data_5m = get_data(args)
        df = data_5m.copy()
        df["price"] = df["close"]

        df["risk"] = df["price"].rolling(288 * 1 // 4, min_periods=1).mean().dropna()
        df["riskmetric"] = df["risk"]

        checked_values_after_before = 5
        df["min"] = df.iloc[
            argrelextrema(df.riskmetric.values, np.less_equal, order=checked_values_after_before)[0]
        ]["riskmetric"]
        df["max"] = df.iloc[
            argrelextrema(
                df.riskmetric.values, np.greater_equal, order=checked_values_after_before
            )[0]
        ]["riskmetric"]

        df = df[["riskmetric", "price", "min", "max"]]
        riskmetric_df = df[df["riskmetric"].notna()]
        return riskmetric_df[self.steps[0] : self.steps[-1]]

    def execute_step(self):
        super().execute_step()
        local_min = self.riskmetric.loc[self.current_step]["min"]
        local_max = self.riskmetric.loc[self.current_step]["max"]

        # We are at local minimum
        if not pd.isnull(local_min):
            self.buy()
        # We are at local maximum
        elif not pd.isnull(local_max):
            self.sell()
