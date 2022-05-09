"""
File defining the DCA strategy.
"""


from .strategy import Strategy
from .utils import Portfolio, TradingData


class DCAStrategy(Strategy):
    def __init__(self, data: TradingData, portfolio: Portfolio = None, **kwargs):
        super().__init__(data, portfolio)
        self.dca_interval = kwargs.get("dca_interval", 1)
        self.base_buy = kwargs.get("base", 5)
        self.interval_until_next_buy = self.dca_interval
        self.name += f"{{interval: {self.dca_interval}}}"

        print(self.base_buy)
        # print(self.base_buy * len(self.steps))

    def execute_step(self):
        super().execute_step()
        self.interval_until_next_buy -= 1
        if self.interval_until_next_buy == 0:
            self.execute_dca()
            self.interval_until_next_buy = self.dca_interval

    def execute_dca(self):
        self.buy_additional(self.base_buy)

    def log_profits(self):
        profit_in_usd = self.get_profit_in_usd()
        if profit_in_usd == 0 and self.total_usd_invested == 0:
            self.profits_in_time[self.i] = 0
        else:
            self.profits_in_time[self.i] = profit_in_usd / self.total_usd_invested
