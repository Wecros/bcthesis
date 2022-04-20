"""
File defining the risk metric strategy.
"""

import plotly.graph_objs as go
from plotly.subplots import make_subplots

from simulation import Simulation


class HodlStrategy(Simulation):
    def __init__(self, data, cash: int = 1000):
        super().__init__(data, cash)
        # self.rebalance_ratio = 'even'
        self.buy()

    def execute_step(self):
        super().execute_step()

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
            fig.add_trace(go.Scatter(x=self.steps, y=self.data.loc[coin].close, name=coin))
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
