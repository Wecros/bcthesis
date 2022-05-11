"""
File defining the HODL strategy.
"""


from .strategy import Strategy
from .utils import Portfolio, TradingData


class HodlStrategy(Strategy):
    """Very simple class, buying all coins at first date and logging results of each day.

    RFE: Optimization could be used in a form of vectorized computation, since there is
    no need to compute each step of such simple strategy individually.
    """

    def __init__(self, data: TradingData, portfolio: Portfolio = None):
        super().__init__(data, portfolio)
        self.buy()

    def execute_step(self):
        super().execute_step()
