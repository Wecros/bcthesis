"""
File for orchestrating the various strategies in play.
"""

import logging

import plotly.express as px
import plotly.graph_objs as go
from plotly.subplots import make_subplots

from plotter import Plotter
from riskmetric_strategy import RiskMetricStrategy
from utils import Strategy, get_dates_from_index


def simulate(data):
    logging.info("Running simulation")

    # plot_all_coins(data)

    strategy = RiskMetricStrategy(data)
    strategy.run_strategy()
    print(strategy.stats())
    # strategy.plot().show()

    strat = Strategy(name=type(strategy).__name__, profits=strategy.profits_in_time)

    strategies = [strat]

    plotter = Plotter(data, strategies)
    plotter.plot_strategies_with_data()
    plotter.show()


def plot_strategies(data, strategies: list):
    dates = get_dates_from_index(data)
    fig = make_subplots()
    fig.update_layout(title_text="Rebalance Analysis")
    fig.update_xaxes(title_text="1 day interval")
    fig.update_yaxes(title_text="USD value")

    for strategy in strategies:
        plot_strategy(data, strategy, fig, dates)

    fig.update_yaxes(type="log")
    return fig


def plot_strategy(data, strategy, fig, dates):
    fig.add_trace(
        go.Scatter(
            x=dates,
            y=strategy.profits_in_time,
            mode="lines",
            name="Profit in USD",
            line=dict(color="rgba(46, 204, 113, 1.9)", width=4),
        )
    )


def plot_all_coins(data):
    fig = px.line(data.reset_index(), x="open_time", y="close", color="pair", log_y=True)
    fig.show()
