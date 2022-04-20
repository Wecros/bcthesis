"""
Module defining the plotter class used for plotting graphs.
"""


import numpy.typing as npt
import pandas as pd
import plotly.graph_objs as go
from plotly.subplots import make_subplots

from utils import Strategy, get_dates_from_index, get_symbols_from_index


class Plotter:
    """Plotter class.

    plot_* functions serve to customize the self.figure object.
    """

    def __init__(self, data, strategies):
        self.figure = make_subplots()
        self.data = data
        self.dates: npt.NDArray[pd.Timestamp] = get_dates_from_index(data)
        self.symbols: list[str] = get_symbols_from_index(data)
        self.strategies: list[Strategy] = strategies

    def plot_strategies_with_data(self):
        self.figure = make_subplots()

        self.plot_data()
        self.plot_strategies()

        self.figure.update_layout(title_text="Layout Title")
        self.figure.update_xaxes(title_text="X axis title")
        self.figure.update_yaxes(title_text="Y axis title")
        self.figure.update_yaxes(type="log")

    def plot_data(self):
        for symbol in self.symbols:
            self._plot_symbol(symbol)

    def _plot_symbol(self, symbol: str):
        self.figure.add_trace(
            go.Scatter(x=self.dates, y=self.data.loc[symbol, "close"], name=symbol)
        )

    def plot_strategies(self):
        for strategy in self.strategies:
            self._plot_strategy(strategy)

    def _plot_strategy(self, strategy: Strategy):
        self.figure.add_trace(
            go.Scatter(x=self.dates, y=strategy.profits, mode="lines", name=strategy.name)
        )

    def get_figure(self):
        return self.figure

    def show(self):
        return self.figure.show()
