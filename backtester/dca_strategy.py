"""
File defining the DCA strategy.
"""


from .strategy import Strategy
from .utils import Portfolio, TradingData


class DCAStrategy(Strategy):
    def __init__(self, data: TradingData, portfolio: Portfolio = None, **kwargs):
        super().__init__(data, portfolio)
        self.dca_interval = kwargs.get("dca_interval", 1)
        self.interval_until_next_buy = self.dca_interval
        self.name += f"{{interval: {self.dca_interval}}}"

    def execute_step(self):
        super().execute_step()
        self.interval_until_next_buy -= 1
        if self.interval_until_next_buy == 0:
            self.buy_additional(100)
            self.interval_until_next_buy = self.dca_interval

    def buy_additional(self, usd: float):
        coins = self.portfolio.coins
        usd_to_buy_coin_with = usd / len(coins)
        for coin in coins:
            close = self.get_close_value(coin)
            coins[coin] += usd_to_buy_coin_with / close
        self.total_usd_invested += usd
