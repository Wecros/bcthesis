"""
Author: Marek Filip 2022

File defining the risk metric strategy.
"""


from .strategy import Strategy
from .utils import Portfolio, TradingData


class RebalanceStrategy(Strategy):
    """Class for simulating the rebalance strategy. It is a periodic rebalance with the "interval'
    being an adjustable argument.
    """

    def __init__(self, data: TradingData, portfolio: Portfolio = None, **kwargs):
        super().__init__(data, portfolio)
        self.rebalance_interval = kwargs.get("interval", 1)
        # self.rebalance_ratio = 'even'
        self.rebalance_ratio = 100 / len(self.portfolio.coins)
        self.interval_until_next_rebalance = self.rebalance_interval
        self.buy()
        self.name += f"{{interval: {self.rebalance_interval}}}"

    def execute_step(self):
        super().execute_step()
        self.interval_until_next_rebalance -= 1
        if self.interval_until_next_rebalance == 0:
            self.rebalance_coins()
            self.interval_until_next_rebalance = self.rebalance_interval

    def rebalance_coins(self):
        """Do the rebalance, equal reatio between all coins."""
        usd_to_rebalance = self.get_coins_value_in_usd()
        self.portfolio.coins = {coin: 0 for coin in self.portfolio.coins}
        usd_per_coin = usd_to_rebalance / len(self.portfolio.coins)
        for coin in self.portfolio.coins:
            close = self.get_close_value(coin)
            self.portfolio.coins[coin] = usd_per_coin / close

    def print_rebalance_ratios(self):
        coins = self.portfolio.coins
        coins_to_usd = {}
        for coin in coins:
            close = self.get_close_value(coin)
            coins_to_usd[coin] = close * coins[coin]
        total_usd = sum(coins_to_usd.values())
        coins_percentages = {}
        for coin in coins:
            close = self.get_close_value(coin)
            coins_percentages[coin] = coins_to_usd[coin] / total_usd

        print(total_usd)
        print(coins_to_usd)
        print(coins_percentages)
