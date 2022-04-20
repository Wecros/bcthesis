"""
File defining the risk metric strategy.
"""

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
from plotly.subplots import make_subplots

from simulation import Simulation
from utils import get_dates_from_index


class RiskMetricStrategy(Simulation):
    def __init__(self, data, cash: int = 1000):
        super().__init__(data, cash)
        self.riskmetric = get_risk_metric(data)
        self.threshold = 0.7
        self.states = {
            "sell": False,
            0.7: False,
            0.6: False,
            0.5: False,
            0.4: False,
            0.3: False,
            0.2: False,
            0.1: False,
        }

    def execute_step(self):
        super().execute_step()
        risk = self.riskmetric.loc[self.current_step]["avg"]

        if risk < 0.1:
            if not self.states[0.1]:
                self.states = self.set_states(0.1)
                self.sell()
                self.buy()
        elif risk < 0.2:
            if not self.states[0.2]:
                self.states = self.set_states(0.2)
                self.sell()
                self.buy()
        elif risk < 0.3:
            if not self.states[0.3]:
                self.states = self.set_states(0.3)
                self.sell()
                self.buy()
        elif risk < 0.4:
            if not self.states[0.4]:
                self.states = self.set_states(0.4)
                self.buy_percentage(0.8)
        elif risk < 0.5:
            if not self.states[0.5]:
                self.states = self.set_states(0.5)
                self.buy_percentage(0.6)
        elif risk < 0.6:
            if not self.states[0.6]:
                self.states = self.set_states(0.6)
                self.buy_percentage(0.4)
        elif risk < 0.7:
            if not self.states[0.7]:
                self.states = self.set_states(0.7)
                self.buy_percentage(0.2)
        else:
            if not self.sold_state:
                self.sell()
                self.sold_state = True
                self.bought_state = True

    def set_states(self, state_to_set):
        self.states = {k: False for k in self.states}
        self.states[state_to_set] = True
        self.sold_state = False
        return self.states

    def buy(self):
        super().buy()

    def sell(self):
        super().sell()

    def buy_percentage(self, percent):
        self.bought_dates.append(self.current_step)
        coins = self.portfolio.coins

        # print(self.riskmetric.loc[self.current_step]['avg'])
        # print(self.current_step)
        # print(self.portfolio.usd)
        # print(coins)

        self.sell()

        # print(self.portfolio.usd)
        # print(coins)

        usd_to_buy_coins_with = self.portfolio.usd * percent
        usd_to_buy_one_coin_with = usd_to_buy_coins_with / len(coins)
        for coin in coins:
            close = self.getCloseValue(coin)
            self.portfolio.coins[coin] += usd_to_buy_one_coin_with / close

        self.portfolio.usd = self.portfolio.usd - usd_to_buy_coins_with

        # print(usd_to_buy_coins_with, usd_to_buy_one_coin_with)
        # print(coins)
        # print(self.portfolio.usd)
        # print()

    def transfer_coins_to_stablecoin(self, percent):
        self.sold_dates.append(self.current_step)
        coins = self.portfolio.coins

        for coin in coins:
            close = self.getCloseValue(coin)
            coin_left = self.portfolio.coins[coin] * percent
            coin_to_buy_usd_with = self.portfolio.coins[coin] - coin_left

            self.portfolio.usd += coin_to_buy_usd_with * close
            self.portfolio.coins[coin] = coin_left

    def plot(self):
        self.riskmetric.avg * self.data.loc["BTCUSDT"]["open"]
        self.portfolio.coins

        # Create figure with secondary y-axis
        fig = make_subplots(specs=[[{"secondary_y": True}]])

        # Add figure title
        fig.update_layout(title_text="Risk Metric Analysis")
        fig.update_xaxes(title_text="1 day interval")
        fig.update_yaxes(title_text="USD value", secondary_y=False)
        fig.update_yaxes(title_text="Risk Metric Scale", secondary_y=True)

        fig.add_trace(
            go.Scatter(x=self.steps, y=self.riskmetric.avg, name="risk metric"),
            secondary_y=True,
        )
        fig.add_hline(
            y=self.threshold,
            name="risk metric threhsold",
            annotation_text="threshold",
            secondary_y=True,
        )

        fig = px.scatter(
            self.riskmetric,
            x=self.riskmetric.index,
            y="Value",
            color="avg",
            color_continuous_scale="turbo",
        )
        fig.update_yaxes(title="Price ($USD)", type="log", showgrid=False)
        fig.update_layout(template="seaborn")

        fig.add_trace(
            go.Scatter(
                x=self.steps,
                y=self.profits_in_time,
                mode="lines",
                name="Profit in USD",
                line=dict(color="rgba(46, 204, 113, 1.9)", width=4),
            )
        )

        dates = get_dates_from_index(self.data)
        indeces = map(lambda x: list(dates).index(x), self.bought_dates)
        profits_bought = list(map(lambda x: self.profits_in_time[x], indeces))
        print(profits_bought)

        fig.add_trace(
            go.Scatter(
                x=np.array(self.bought_dates),
                y=profits_bought,
                mode="markers",
                name="bought",
                marker_symbol="triangle-up",
                marker=dict(
                    color="green",
                    size=15,
                ),
            ),
        )
        fig.add_trace(
            go.Scatter(
                x=np.array(self.sold_dates),
                y=self.profits_in_time,
                mode="markers",
                name="sold",
                marker_symbol="triangle-down",
                marker=dict(
                    color="red",
                    size=15,
                ),
            ),
        )

        return fig


def get_risk_metric(data):
    """Get risk metric relevant for the data's date range."""
    df = pd.read_csv("btc.csv", index_col=0)
    # Calculate the `Risk Metric`
    df = pd.read_csv("btc.csv", index_col=0)
    df["MA"] = df["Value"].rolling(374, min_periods=1).mean().dropna()
    df["preavg"] = (np.log(df["Value"]) - np.log(df["MA"])) * df.index**0.395

    # Normalization to 0-1 range
    df["avg"] = (df["preavg"] - df["preavg"].cummin()) / (
        df["preavg"].cummax() - df["preavg"].cummin()
    )

    df = df.set_index(df["Date"])
    df = df.drop(columns=["Date"])
    df.index = df.index.map(pd.to_datetime)

    date_index = get_dates_from_index(data)
    useful_riskmetric = df[date_index[0] : date_index[-1]]
    return useful_riskmetric
