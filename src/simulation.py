"""
File defining the abstract class that serves as a template for simulation strategies.
"""

from abc import ABC, abstractmethod

import numpy as np
import pandas as pd

from utils import Portfolio, get_dates_from_index, get_symbols_from_index


class Simulation(ABC):
    @abstractmethod
    def __init__(self, data: pd.DataFrame, cash: int = 1000):
        self.bought_state: bool = False
        self.sold_state: bool = True
        self.bought_dates: list[pd.Timestamp] = []
        self.sold_dates: list[pd.Timestamp] = []
        self.steps: np.ndarray = get_dates_from_index(data)
        self.current_step: pd.Timestamp = self.steps[0]
        self.i = 0
        self.portfolio = Portfolio(usd=cash, coins={k: 0 for k in get_symbols_from_index(data)})
        self.data = data
        self.profits_in_time: np.ndarray = np.zeros(self.steps.size)
        self.total_usd_invested = cash

    def flip_bought_sold_states(self):
        self.bought_state = not self.bought_state
        self.sold_state = not self.sold_state

    def run_strategy(self):
        while self.i != self.steps.size:
            self.current_step = self.steps[self.i]
            self.execute_step()
            self.i += 1

    @abstractmethod
    def execute_step(self):
        ...
        # print(self.current_step)
        self.profits_in_time[self.i] = self.getProfitInUSD()

    @abstractmethod
    def buy(self):
        # if self.bought_state:
        # logging.info(f"Tried to buy with a bought state, step: {self.current_step}")
        # return
        self.bought_dates.append(self.current_step)
        # self.flip_bought_sold_states()

        coins = self.portfolio.coins
        usd_per_coin = self.portfolio.usd / len(coins)
        for coin in coins:
            close = self.getCloseValue(coin)
            coins[coin] = usd_per_coin / close
        self.portfolio.usd = 0

    @abstractmethod
    def sell(self):
        # if self.sold_state:
        # logging.info(f"Tried to sell with a sold state, step: {self.current_step}")
        # return
        # self.sold_dates.append(self.current_step)
        # self.flip_bought_sold_states()

        coins = self.portfolio.coins
        for coin in coins:
            close = self.getCloseValue(coin)
            self.portfolio.usd += self.portfolio.coins[coin] * close
            self.portfolio.coins[coin] = 0

    def getCloseValue(self, coin):
        # return self.data.loc[(self.current_step, coin), 'close']
        # return self.data.loc[[(self.current_step, coin)]].close[0]
        return self.data.loc[[(coin, self.current_step)]].close[0]

    def getProfitInUSD(self):
        """Gain total portfolio profit in USD relevant to the current step."""
        coin_profit = sum(
            self.portfolio.coins[coin] * self.getCloseValue(coin) for coin in self.portfolio.coins
        )
        return self.portfolio.usd + coin_profit

    def getProfitInBTC(self):
        """Gain total portfolio profit in BTC relevant to the current step."""
        ...

    def plot(self):
        ...

    def stats(self):
        profitInUSD = self.getProfitInUSD()
        return (
            f"Strategy: {type(self).__name__}\n"
            f"Profit in USD: {profitInUSD}\n"
            f"Total USD invested: {self.total_usd_invested}\n"
            f"Ratio of profit to total USD invested (higher is better):"
            f"{profitInUSD / self.total_usd_invested}"
        )
