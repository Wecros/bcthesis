"""
Author: Marek Filip 2022

File defining the DCA strategy optimized for risk metric.
"""


from abc import ABC, abstractmethod

from .riskmetric_strategy import RiskMetricStrategy
from .utils import Portfolio, TradingData


class DCARiskMetricStrategy(ABC, RiskMetricStrategy):
    """Abstract class implementing the dollar-cost averaging simulation that takes risk metric
    into account. It is used as base for other classes.
    """

    def __init__(self, data: TradingData, portfolio: Portfolio = None, *args, **kwargs):
        super().__init__(data, portfolio, *args, **kwargs)
        self.dca_interval = kwargs.get("dca_interval", 1)
        self.interval_until_next_buy = self.dca_interval
        self.name += f"{{interval: {self.dca_interval}}}"
        self.base_buy = 5

    def execute_step(self):
        super().execute_step()
        self.interval_until_next_buy -= 1
        if self.interval_until_next_buy == 0:
            self.execute_dca()
            self.interval_until_next_buy = self.dca_interval

    def log_profits(self):
        profit_in_usd = self.get_profit_in_usd()
        if profit_in_usd == 0 and self.total_usd_invested == 0:
            self.profits_in_time[self.i] = 0
        else:
            self.profits_in_time[self.i] = profit_in_usd / self.total_usd_invested

    @abstractmethod
    def execute_dca(self):
        pass


class DCARiskMetricStrategy7to0(DCARiskMetricStrategy):
    """Class implementing the dollar-cost averaging simulation risk metric simulation
    with linera 7 to 0 buying power decrease.
    """

    def execute_dca(self):
        risk = self.riskmetric.loc[self.current_step]["riskmetric"]

        if risk < 0.1:
            self.buy_additional(self.base_buy * 7)
        elif risk < 0.2:
            self.buy_additional(self.base_buy * 6)
        elif risk < 0.3:
            self.buy_additional(self.base_buy * 5)
        elif risk < 0.4:
            self.buy_additional(self.base_buy * 4)
        elif risk < 0.5:
            self.buy_additional(self.base_buy * 3)
        elif risk < 0.6:
            self.buy_additional(self.base_buy * 2)
        elif risk < 0.7:
            self.buy_additional(self.base_buy * 1)
        elif risk < 0.8:
            self.buy_additional(self.base_buy * 0)
        elif risk < 0.9:
            self.buy_additional(self.base_buy * 0)
        else:
            self.buy_additional(self.base_buy * 0)


class DCARiskMetricStrategyFibonacci(DCARiskMetricStrategy):
    """Class implementing the dollar-cost averaging simulation risk metric simulation
    with Fibonacci optimization in mind.
    """

    def execute_dca(self):
        risk = self.riskmetric.loc[self.current_step]["riskmetric"]

        if risk < 0.1:
            self.buy_additional(self.base_buy * 34)
        elif risk < 0.2:
            self.buy_additional(self.base_buy * 21)
        elif risk < 0.3:
            self.buy_additional(self.base_buy * 13)
        elif risk < 0.4:
            self.buy_additional(self.base_buy * 8)
        elif risk < 0.5:
            self.buy_additional(self.base_buy * 5)
        elif risk < 0.6:
            self.buy_additional(self.base_buy * 3)
        elif risk < 0.7:
            self.buy_additional(self.base_buy * 2)
        elif risk < 0.8:
            self.buy_additional(self.base_buy * 1)
        elif risk < 0.9:
            self.buy_additional(self.base_buy * 1)
        else:
            self.buy_additional(self.base_buy * 0)


class DCARiskMetricStrategyFibonacciAdjusted(DCARiskMetricStrategy):
    """Class implementing the dollar-cost averaging simulation risk metric simulation
    with adjust Fibonacci sequence.
    """

    def execute_dca(self):
        risk = self.riskmetric.loc[self.current_step]["riskmetric"]

        if risk < 0.1:
            self.buy_additional(self.base_buy * 21)
        elif risk < 0.2:
            self.buy_additional(self.base_buy * 13)
        elif risk < 0.3:
            self.buy_additional(self.base_buy * 8)
        elif risk < 0.4:
            self.buy_additional(self.base_buy * 5)
        elif risk < 0.5:
            self.buy_additional(self.base_buy * 3)
        elif risk < 0.6:
            self.buy_additional(self.base_buy * 2)
        elif risk < 0.7:
            self.buy_additional(self.base_buy * 1)
        elif risk < 0.8:
            self.buy_additional(self.base_buy * 0)
        elif risk < 0.9:
            self.buy_additional(self.base_buy * 0)
        else:
            self.buy_additional(self.base_buy * 0)
