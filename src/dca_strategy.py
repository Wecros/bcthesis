"""
File defining the DCA strategy.
"""

import numpy as np
import plotly.graph_objs as go
from plotly.subplots import make_subplots

from simulation import Simulation


class DCAStrategy(Simulation):
    def __init__(self, data, cash: int = 1000):
        super().__init__(data, cash)
        self.dca_interval_in_days = 1
        self.dca_days_until_next_buy = self.dca_interval_in_days
        self.total_usd_invested = cash

    def execute_step(self):
        super().execute_step()
        self.dca_days_until_next_buy -= 1
        if self.dca_days_until_next_buy == 0:
            self.buy_additional(100)
            self.dca_days_until_next_buy = self.dca_interval_in_days

    def buy_additional(self, usd: float):
        coins = self.portfolio.coins
        usd_to_buy_coin_with = usd / len(coins)
        for coin in coins:
            close = self.getCloseValue(coin)
            coins[coin] += usd_to_buy_coin_with / close
        self.total_usd_invested += usd

    def buy(self):
        ...

    def sell(self):
        ...

    def plot(self):
        np.array(self.steps)
        coins = self.portfolio.coins

        fig = make_subplots()
        fig.update_layout(title_text="DCA Analysis")
        fig.update_xaxes(title_text="1 day interval")
        fig.update_yaxes(title_text="USD value")

        for coin in coins:
            # fig.add_trace(go.Scatter(x=self.steps, y=self.data.loc[coin].close, name=coin))
            fig.add_trace(
                go.Scatter(
                    x=self.steps,
                    y=self.data.reset_index()
                    .set_index(["pair", "open_time"])
                    .sort_index()
                    .loc[coin]
                    .close,
                    name=coin,
                )
            )
        fig.add_trace(
            go.Scatter(
                x=self.steps,
                y=self.profits_in_time,
                mode="lines",
                name="Profit in USD",
                line=dict(color="rgba(46, 204, 113, 1.9)", width=4),
            )
        )
        # fig.update_yaxes(type="log")

        return fig
