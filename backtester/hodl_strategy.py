"""
File defining the risk metric strategy.
"""


from .strategy import Strategy
from .utils import Portfolio, TradingData


class HodlStrategy(Strategy):
    def __init__(self, data: TradingData, portfolio: Portfolio = None):
        super().__init__(data, portfolio)
        self.buy()

    def execute_step(self):
        super().execute_step()
