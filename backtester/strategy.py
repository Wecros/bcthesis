"""
File defining the abstract class that serves as a template for strategy simulations.
"""

import logging
from abc import ABC, abstractmethod

import numpy as np
import numpy.typing as npt
import pandas as pd

from .utils import BTC_SYMBOL, Portfolio, TradingData, create_portfolio_from_data


class Strategy(ABC):
    @abstractmethod
    def __init__(self, data: TradingData, portfolio: Portfolio = None):
        self.i = 0
        self.data = data.data
        self.trading_vars = data.variables
        self.steps: npt.NDArray[pd.Timestamp] = data.dates
        self.current_step: pd.Timestamp = self.steps[self.i]
        self.profits_in_time: npt.NDArray[float] = np.zeros(self.steps.size)
        self.name = type(self).__name__

        self.portfolio = portfolio
        if self.portfolio is None:
            self.portfolio = create_portfolio_from_data(data)
        self.total_usd_invested = self.portfolio.usd

        self.bought_dates: list[pd.Timestamp] = []
        self.sold_dates: list[pd.Timestamp] = []

    def run_simulation(self):
        while self.i != self.steps.size:
            self.current_step = self.steps[self.i]
            self.execute_step()
            self.i += 1

    @abstractmethod
    def execute_step(self):
        self.log_profits()

    def log_profits(self):
        self.profits_in_time[self.i] = self.get_profit_in_usd()

    def buy(self):
        if self.portfolio.usd == 0:
            logging.debug(f"Tried to buy with 0 dollars, step: {self.current_step}")
            return -1
        self.bought_dates.append(self.current_step)
        self.execute_buy_logic()
        return 0

    def execute_buy_logic(self):
        coins = self.portfolio.coins
        usd_per_coin = self.portfolio.usd / len(coins)
        for coin in coins:
            close = self.get_close_value(coin)
            coins[coin] += usd_per_coin / close
        self.portfolio.usd = 0

    def sell(self):
        if all(value == 0 for value in self.portfolio.coins.values()):
            logging.debug(f"Tried to sell with 0 $USD in coins, step: {self.current_step}")
            return -1
        self.sold_dates.append(self.current_step)
        self.execute_sell_logic()
        return 0

    def execute_sell_logic(self):
        coins = self.portfolio.coins
        for coin in coins:
            close = self.get_close_value(coin)
            self.portfolio.usd += self.portfolio.coins[coin] * close
            self.portfolio.coins[coin] = 0

    def buy_partial(self, percentage):
        """Buy only a partial percentage of the coins. Keep the rest in stablecoins.
        The percantage is always calculated from the total sum of coins + stablecoins.

        NOTE: If you want to partially sell, just inverse the wanted percentage on buy_partial()
        sell() <=> buy_partial(0)
        buy() <=> buy_partial(100)
        buy_partial(90) <=> "sell_partial(10)"
        """
        assert 0 <= percentage <= 100
        self.bought_dates.append(self.current_step)
        return self._execute_partial_logic(percentage)

    def sell_partial(self, percentage):
        """Sell only a partial percentage of the coins. Keep the rest in coins.
        The percantage is always calculated from the total sum of coins + stablecoins.
        """
        assert 0 <= percentage <= 100
        self.sold_dates.append(self.current_step)
        return self._execute_partial_logic(100 - percentage)

    def _execute_partial_logic(self, percentage):
        """Execute partial buy."""
        coins = self.portfolio.coins
        ratio = percentage / 100
        assert 0 <= ratio <= 1

        # Execute the sell so that we have all USD available - technically also do rebalance
        self.execute_sell_logic()

        usd_to_buy_coins_with = self.portfolio.usd * ratio
        usd_to_buy_one_coin_with = usd_to_buy_coins_with / len(coins)
        for coin in coins:
            close = self.get_close_value(coin)
            self.portfolio.coins[coin] += usd_to_buy_one_coin_with / close

        self.portfolio.usd = self.portfolio.usd - usd_to_buy_coins_with

    def buy_additional(self, usd: float):
        """Buy additional coins using new income. Used for DCA types of stratgies."""
        self.bought_dates.append(self.current_step)
        coins = self.portfolio.coins
        usd_to_buy_coin_with = usd / len(coins)
        for coin in coins:
            close = self.get_close_value(coin)
            coins[coin] += usd_to_buy_coin_with / close
        self.total_usd_invested += usd

    def get_close_value(self, coin: str):
        """Get close value of a coin relevant to the current step."""
        # return self.data.loc[[(self.current_step, coin)]].close[0]
        return self.data.loc[[(coin, self.current_step)]]["close"][0]

    def get_profit_in_usd(self):
        """Gain total portfolio profit in USD relevant to the current step."""
        return self.portfolio.usd + self.get_coins_value_in_usd()

    def get_coins_value_in_usd(self):
        return sum(
            self.portfolio.coins[coin] * self.get_close_value(coin) for coin in self.portfolio.coins
        )

    def get_profit_in_btc(self):
        """Gain total portfolio profit in BTC relevant to the current step."""
        coin = BTC_SYMBOL
        close = self.get_close_value(coin)
        profit = self.get_profit_in_usd()
        return profit / close

    def stats(self):
        profitInUSD = self.profits_in_time[-1]
        return (
            f"Strategy: {type(self).__name__}\n"
            f"Profit in USD: {profitInUSD}\n"
            f"Profit in BTC: {self.get_profit_in_btc()}\n"
            f"Total USD invested: {self.total_usd_invested}\n"
            f"Ratio of profit to total USD invested (higher is better): "
            f"{profitInUSD / self.total_usd_invested}"
        )
