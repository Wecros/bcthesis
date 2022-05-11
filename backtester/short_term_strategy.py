"""
File defining the short term strategy.
"""


import numpy as np
import pandas as pd
from scipy.signal import argrelextrema

from .api_downloader import get_data
from .strategy import Strategy
from .utils import Portfolio, TradingData, get_symbols_from_index


class ShortTermStrategyIdeal(Strategy):
    def __init__(self, data: TradingData, portfolio: Portfolio = None, *args, **kwargs):
        super().__init__(data, portfolio)
        self.riskmetric = self.compute_metric()
        self.buy()

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

        checked_values_after_before = 3
        df["min_plot"] = df.iloc[
            argrelextrema(df.riskmetric.values, np.less_equal, order=checked_values_after_before)[0]
        ]["risk"]
        df["max_plot"] = df.iloc[
            argrelextrema(
                df.riskmetric.values, np.greater_equal, order=checked_values_after_before
            )[0]
        ]["risk"]

        df["riskmetric"] = (df["risk"] - df["risk"].cummin()) / (
            df["risk"].cummax() - df["risk"].cummin()
        )

        checked_values_after_before = 3
        df["min"] = df.iloc[
            argrelextrema(df.riskmetric.values, np.less_equal, order=checked_values_after_before)[0]
        ]["riskmetric"]
        df["max"] = df.iloc[
            argrelextrema(
                df.riskmetric.values, np.greater_equal, order=checked_values_after_before
            )[0]
        ]["riskmetric"]
        df["min_real"] = df["min"].shift(checked_values_after_before)
        df["max_real"] = df["max"].shift(checked_values_after_before)

        df = df[
            [
                "risk",
                "riskmetric",
                "price",
                "min",
                "max",
                "min_real",
                "max_real",
                "min_plot",
                "max_plot",
            ]
        ]
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


class ShortTermStrategyReal(ShortTermStrategyIdeal):
    def execute_step(self):
        super(ShortTermStrategyIdeal, self).execute_step()
        local_min = self.riskmetric.loc[self.current_step]["min_real"]
        local_max = self.riskmetric.loc[self.current_step]["max_real"]

        # We are at local minimum
        if not pd.isnull(local_min):
            self.buy()
        # We are at local maximum
        elif not pd.isnull(local_max):
            self.sell()


class ShortTermStrategyAdjusted(ShortTermStrategyIdeal):
    def __init__(self, data: TradingData, portfolio: Portfolio = None, *args, **kwargs):
        super().__init__(data, portfolio, *args, **kwargs)
        self.last_action_risk = self.riskmetric.loc[self.current_step]["riskmetric"]
        self.last_action_price = self.data.loc[("BTCUSDT", self.current_step), "close"]
        self.bitcoin_riskmetric = kwargs.get("riskmetric")
        self.riskmetric = self.compute_metric()
        self.risks = []
        self.is_rising = False
        self.is_falling = False

        self.execute_empty_step()
        if (
            self.riskmetric.loc[self.steps[self.i]]["riskmetric"]
            > self.riskmetric.loc[self.steps[0]]["riskmetric"]
        ):
            self.is_rising = True
        else:
            self.is_falling = True
        print(
            self.riskmetric.loc[self.steps[self.i]]["riskmetric"],
            self.riskmetric.loc[self.steps[0]]["riskmetric"],
            self.is_rising,
            self.is_falling,
        )

    def execute_step(self):
        super(ShortTermStrategyIdeal, self).execute_step()
        self.execute_risk_logic()

    def execute_empty_step(self):
        self.log_profits()
        self.i += 1
        risk = self.riskmetric.loc[self.current_step]["riskmetric"]
        self.risks.append(risk)

    @staticmethod
    def is_value_larger_than_last_list(value, input_list, n=3):
        return all(value > el for el in input_list[-n:])

    @staticmethod
    def is_value_smaller_than_last_list(value, input_list, n=3):
        return all(value < el for el in input_list[-n:])

    def is_risk_rising(self, n=1):
        return all(
            previous <= following
            for previous, following in zip(self.risks[-n - 1 :], self.risks[-n:])
        )

    def is_risk_lowering(self, n=1):
        return all(
            previous >= following
            for previous, following in zip(self.risks[-n - 1 :], self.risks[-n:])
        )

    def execute_risk_logic(self):
        # btc_riskmetric = self.real_riskmetric.loc[self.current_step.normalize()]['riskmetric']
        risk = self.riskmetric.loc[self.current_step]["riskmetric"]
        self.get_close_value("BTCUSDT")

        self.riskmetric.loc[self.current_step]["min_real"]
        self.riskmetric.loc[self.current_step]["max_real"]

        # We are at local minimum
        if self.is_value_larger_than_last_list(risk, self.risks, n=1) and self.is_risk_lowering(
            n=5
        ):
            # if abs(self.last_action_risk - risk) < 0.001:
            # return
            print(self.current_step, "min")
            self.buy()
            self.last_action_risk = risk
            self.last_action_price = self.data.loc[("BTCUSDT", self.current_step), "close"]
        # We are at local maximum
        if self.is_value_smaller_than_last_list(risk, self.risks, n=1) and self.is_risk_rising(n=5):
            if abs(self.last_action_risk - risk) < 0.001:
                return

            print(self.current_step, "max")
            self.sell()
            self.last_action_risk = risk
            self.last_action_price = self.data.loc[("BTCUSDT", self.current_step), "close"]

        self.risks.append(risk)
