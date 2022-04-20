"""
File defining the risk metric strategy.
"""

import plotly.graph_objs as go
from plotly.subplots import make_subplots

from simulation import Simulation


class RebalanceStrategy(Simulation):
    def __init__(self, data, cash: int = 1000):
        super().__init__(data, cash)
        # self.rebalance_ratio = 'even'
        self.rebalance_ratio = 100 / len(self.portfolio.coins)
        self.rebalance_interval = 1
        self.interval_until_next_rebalance = self.rebalance_interval
        self.buy()

    def execute_step(self):
        super().execute_step()
        self.interval_until_next_rebalance -= 1
        if self.interval_until_next_rebalance == 0:
            self.rebalance()
            self.interval_until_next_rebalance = self.rebalance_interval

    def rebalance(self):
        # self.print_rebalance_ratios()
        self.sell()
        self.buy()

    def print_rebalance_ratios(self):
        coins = self.portfolio.coins
        coins_to_usd = {}
        for coin in coins:
            close = self.getCloseValue(coin)
            coins_to_usd[coin] = close * coins[coin]
        total_usd = sum(coins_to_usd.values())
        coins_percentages = {}
        for coin in coins:
            close = self.getCloseValue(coin)
            coins_percentages[coin] = coins_to_usd[coin] / total_usd

        print(total_usd)
        print(coins_to_usd)
        print(coins_percentages)

    def buy(self):
        super().buy()

    def sell(self):
        super().sell()

    def plot(self):
        coins = self.portfolio.coins

        fig = make_subplots()
        fig.update_layout(title_text="Rebalance Analysis")
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
        fig.update_yaxes(type="log")

        return fig
