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

        self.bought_state: bool = False
        self.sold_state: bool = True
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
        if self.bought_state:
            logging.info(f"Tried to buy with a bought state, step: {self.current_step}")
            return
        self.set_bought_state()
        self.bought_dates.append(self.current_step)
        self.execute_buy_logic()

    def execute_buy_logic(self):
        coins = self.portfolio.coins
        usd_per_coin = self.portfolio.usd / len(coins)
        for coin in coins:
            close = self.get_close_value(coin)
            coins[coin] = usd_per_coin / close
        self.portfolio.usd = 0

    def sell(self):
        if self.sold_state:
            logging.info(f"Tried to sell with a sold state, step: {self.current_step}")
            return
        self.set_sold_state()
        self.sold_dates.append(self.current_step)
        self.execute_sell_logic()

    def execute_sell_logic(self):
        coins = self.portfolio.coins
        for coin in coins:
            close = self.get_close_value(coin)
            self.portfolio.usd += self.portfolio.coins[coin] * close
            self.portfolio.coins[coin] = 0

    def set_bought_state(self):
        self.bought_state = True
        self.sold_state = False

    def set_sold_state(self):
        self.sold_state = True
        self.bought_state = False

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
        return self.portfolio.coins[coin] / close

    def stats(self):
        profitInUSD = self.profits_in_time[-1]
        return (
            f"Strategy: {type(self).__name__}\n"
            f"Profit in USD: {profitInUSD}\n"
            f"Profit in BTC: {self.get_profit_in_btc()}\n"
            f"Total USD invested: {self.total_usd_invested}\n"
            f"Ratio of profit to total USD invested (higher is better):"
            f"{profitInUSD / self.total_usd_invested}"
        )
