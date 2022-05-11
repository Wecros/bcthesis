"""
File defining the risk metric strategy.
"""


import pandas as pd

from .strategy import Strategy
from .utils import Portfolio, TradingData


class RiskMetricStrategy(Strategy):
    def __init__(self, data: TradingData, portfolio: Portfolio = None, *args, **kwargs):
        super().__init__(data, portfolio)
        self.riskmetric = kwargs.get("riskmetric")

        self.states = {
            "sell": False,
            0.9: False,
            0.8: False,
            0.7: False,
            0.6: False,
            0.5: False,
            0.4: False,
            0.3: False,
            0.2: False,
            0.1: False,
        }

        self.buy()

    def set_states(self, state_to_set):
        self.states = {k: False for k in self.states}
        self.states[state_to_set] = True
        self.sold_state = False
        self.bought_state = False
        return self.states

    def execute_step(self):
        super().execute_step()
        return self.states


class RiskMetricStrategyRiskLogic(RiskMetricStrategy):
    def execute_step(self):
        super(RiskMetricStrategy, self).execute_step()
        self.execute_risk_logic()

    def execute_risk_logic(self):
        risk = self.riskmetric.loc[self.current_step]["riskmetric"]

        if risk < 0.1:
            if not self.states[0.1]:
                self.states = self.set_states(0.1)
                self.buy()
        elif risk < 0.2:
            if not self.states[0.2]:
                self.states = self.set_states(0.2)
                self.buy()
        elif risk < 0.3:
            if not self.states[0.3]:
                self.states = self.set_states(0.3)
                self.buy()
        elif risk < 0.4:
            if not self.states[0.4]:
                self.states = self.set_states(0.4)
                self.buy()
        elif risk < 0.5:
            if not self.states[0.5]:
                self.states = self.set_states(0.5)
                self.buy()
        elif risk < 0.6:
            if not self.states[0.6]:
                self.states = self.set_states(0.6)
                self.buy()
        elif risk < 0.7:
            if not self.states[0.7]:
                self.states = self.set_states(0.7)
                self.buy_partial(100)
        elif risk < 0.8:
            if not self.states[0.8]:
                self.states = self.set_states(0.8)
                self.buy_partial(60)
        elif risk < 0.9:
            if not self.states[0.9]:
                self.states = self.set_states(0.9)
                self.buy_partial(30)
        else:
            if not self.states["sell"]:
                self.states = self.set_states("sell")
                self.sell()


class RiskMetricStrategyIdealExtrema(RiskMetricStrategy):
    def execute_step(self):
        super(RiskMetricStrategy, self).execute_step()
        self.execute_extrema_logic()

    def execute_extrema_logic(self):
        local_min = self.riskmetric.loc[self.current_step]["min"]
        local_max = self.riskmetric.loc[self.current_step]["max"]

        # We are at local minimum
        if not pd.isnull(local_min):
            self.buy()
        # We are at local maximum
        elif not pd.isnull(local_max):
            self.sell()


class RiskMetricStrategyRealExtrema(RiskMetricStrategy):
    def execute_step(self):
        super(RiskMetricStrategy, self).execute_step()
        self.execute_extrema_logic()

    def execute_extrema_logic(self):
        local_min = self.riskmetric.loc[self.current_step]["min_real"]
        local_max = self.riskmetric.loc[self.current_step]["max_real"]

        # We are at local minimum
        if not pd.isnull(local_min):
            self.buy()
        # We are at local maximum
        elif not pd.isnull(local_max):
            self.sell()


class RiskMetricStrategyCombined(RiskMetricStrategy):
    def execute_step(self):
        super(RiskMetricStrategy, self).execute_step()

        local_min = self.riskmetric.loc[self.current_step]["min_real"]
        local_max = self.riskmetric.loc[self.current_step]["max_real"]

        # We are at local minimum
        if not pd.isnull(local_min):
            self.combined_buy()
        # We are at local maximum
        elif not pd.isnull(local_max):
            self.combined_sell()

    def combined_buy(self):
        risk = self.riskmetric.loc[self.current_step]["riskmetric"]

        if risk < 0.1:
            self.buy_partial(100)
        elif risk < 0.2:
            self.buy_partial(100)
        elif risk < 0.3:
            self.buy_partial(100)
        elif risk < 0.4:
            self.buy_partial(100)
        elif risk < 0.5:
            self.buy_partial(100)
        elif risk < 0.6:
            self.buy_partial(100)
        elif risk < 0.7:
            self.buy_partial(100)
        elif risk < 0.8:
            self.buy_partial(80)
        elif risk < 0.9:
            self.buy_partial(60)
        else:
            self.buy_partial(40)

    def combined_sell(self):
        risk = self.riskmetric.loc[self.current_step]["riskmetric"]

        if risk < 0.1:
            self.sell_partial(40)
        elif risk < 0.2:
            self.sell_partial(60)
        elif risk < 0.3:
            self.sell_partial(80)
        elif risk < 0.4:
            self.sell_partial(100)
        elif risk < 0.5:
            self.sell_partial(100)
        elif risk < 0.6:
            self.sell_partial(100)
        elif risk < 0.7:
            self.sell_partial(100)
        elif risk < 0.8:
            self.sell_partial(100)
        elif risk < 0.9:
            self.sell_partial(100)
        else:
            self.sell_partial(100)


class RiskMetricStrategyCombined2(RiskMetricStrategyCombined):
    def combined_buy(self):
        risk = self.riskmetric.loc[self.current_step]["riskmetric"]

        if risk < 0.1:
            self.buy_partial(100)
        elif risk < 0.2:
            self.buy_partial(100)
        elif risk < 0.3:
            self.buy_partial(100)
        elif risk < 0.4:
            self.buy_partial(100)
        elif risk < 0.5:
            self.buy_partial(100)
        elif risk < 0.6:
            self.buy_partial(100)
        elif risk < 0.7:
            self.buy_partial(100)
        elif risk < 0.8:
            self.buy_partial(100)
        elif risk < 0.9:
            self.buy_partial(100)
        else:
            self.buy_partial(100)

    def combined_sell(self):
        risk = self.riskmetric.loc[self.current_step]["riskmetric"]

        if risk < 0.1:
            self.sell_partial(40)
        elif risk < 0.2:
            self.sell_partial(60)
        elif risk < 0.3:
            self.sell_partial(80)
        elif risk < 0.4:
            self.sell_partial(100)
        elif risk < 0.5:
            self.sell_partial(100)
        elif risk < 0.6:
            self.sell_partial(100)
        elif risk < 0.7:
            self.sell_partial(100)
        elif risk < 0.8:
            self.sell_partial(100)
        elif risk < 0.9:
            self.sell_partial(100)
        else:
            self.sell_partial(100)


class RiskMetricStrategyCombined3(RiskMetricStrategyCombined):
    def combined_buy(self):
        risk = self.riskmetric.loc[self.current_step]["riskmetric"]

        if risk < 0.1:
            self.buy_partial(100)
        elif risk < 0.2:
            self.buy_partial(100)
        elif risk < 0.3:
            self.buy_partial(100)
        elif risk < 0.4:
            self.buy_partial(100)
        elif risk < 0.5:
            self.buy_partial(100)
        elif risk < 0.6:
            self.buy_partial(100)
        elif risk < 0.7:
            self.buy_partial(100)
        elif risk < 0.8:
            self.buy_partial(80)
        elif risk < 0.9:
            self.buy_partial(60)
        else:
            self.buy_partial(40)

    def combined_sell(self):
        risk = self.riskmetric.loc[self.current_step]["riskmetric"]

        if risk < 0.1:
            self.sell_partial(100)
        elif risk < 0.2:
            self.sell_partial(100)
        elif risk < 0.3:
            self.sell_partial(100)
        elif risk < 0.4:
            self.sell_partial(100)
        elif risk < 0.5:
            self.sell_partial(100)
        elif risk < 0.6:
            self.sell_partial(100)
        elif risk < 0.7:
            self.sell_partial(100)
        elif risk < 0.8:
            self.sell_partial(100)
        elif risk < 0.9:
            self.sell_partial(100)
        else:
            self.sell_partial(100)
