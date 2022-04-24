"""
Module defining the plotter class used for plotting graphs.
"""


import numpy as np
import numpy.typing as npt
import pandas as pd
import plotly.graph_objs as go
from plotly.subplots import make_subplots

from .riskmetric_strategy import get_risk_metric
from .utils import (
    BTC_SYMBOL,
    OUTPUT_PATH,
    StrategyResult,
    TradingData,
    get_current_datetime_string,
    map_values_to_specific_dates,
)


class Plotter:
    """Plotter class.

    plot_* functions serve to customize the self.figure object.
    """

    def __init__(self, data: TradingData, strategy_results: list[StrategyResult], *args, **kwargs):
        self.figure = make_subplots(*args, **kwargs)
        self.data = data.data
        self.dates: npt.NDArray[pd.Timestamp] = data.dates
        self.symbols: set[str] = data.symbols
        self.strategies: list[StrategyResult] = strategy_results
        self.riskmetric = get_risk_metric(self.dates)

    def plot_strategies_with_data(self):
        self.figure = make_subplots(figure=self.figure)
        self.plot_all_data()
        self.plot_strategies()

    def plot_all_data(self):
        for symbol in self.symbols:
            self._plot_symbol(symbol)

    def _plot_symbol(self, symbol: str):
        self.figure.add_trace(
            go.Scatter(x=self.dates, y=self.data.loc[symbol, "close"], name=symbol)
        )

    def plot_strategies(self):
        for strategy in self.strategies:
            self._plot_strategy(strategy)

    def _plot_strategy(self, strategy: StrategyResult):
        self.figure.add_trace(
            go.Scatter(x=self.dates, y=strategy.profits, mode="lines", name=strategy.name)
        )

    def plot_btc(self):
        self.figure.add_trace(
            go.Scatter(x=self.dates, y=self.data.loc[BTC_SYMBOL, "close"], name=BTC_SYMBOL)
        )

    def plot_colorcoded_riskmetric(self):
        self.figure.add_trace(
            go.Scatter(
                x=self.riskmetric.index,
                y=self.riskmetric["Value"],
                mode="markers",
                marker=dict(
                    color=self.riskmetric["avg"],
                    colorscale="turbo",
                ),
                name="Colordcoded Riskmetric (BTC)",
            )
        )

    def plot_riskmetric_on_second_scale(self):
        self.figure = make_subplots(specs=[[{"secondary_y": True}]], figure=self.figure)
        self.figure.update_yaxes(title_text="Risk Metric Scale", secondary_y=True)
        self.figure.add_trace(
            go.Scatter(x=self.dates, y=self.riskmetric.avg, name="risk metric"), secondary_y=True
        )

    def plot_horizontal_line(self, value, *args, **kwargs):
        self.figure.add_hline(y=value, *args, **kwargs)

    def plot_bought_dates(self):
        for strategy in self.strategies:
            profits_bought = map_values_to_specific_dates(
                self.dates, strategy.sold_dates, strategy.profits
            )
            self.figure.add_trace(
                go.Scatter(
                    x=np.array(strategy.bought_dates),
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

    def plot_sold_dates(self):
        for strategy in self.strategies:
            profits_sold = map_values_to_specific_dates(
                self.dates, strategy.sold_dates, strategy.profits
            )
            self.figure.add_trace(
                go.Scatter(
                    x=np.array(strategy.sold_dates),
                    y=profits_sold,
                    mode="markers",
                    name="sold",
                    marker_symbol="triangle-down",
                    marker=dict(
                        color="red",
                        size=15,
                    ),
                ),
            )

    def plot_log_y(self):
        self.figure.update_yaxes(type="log")

    def plot_log_y_first_axis(self):
        self.figure.update_layout(yaxis=dict(type="log"))

    def plot_log_y_second_axis(self):
        self.figure.update_layout(yaxis2=dict(type="log"))

    def plot_specific_symbols(self, symbol_list):
        for symbol in symbol_list:
            self._plot_symbol(symbol)

    def get_figure(self):
        return self.figure

    def show(self):
        return self.figure.show()

    def save(self, extension="pdf"):
        return self.figure.write_image(OUTPUT_PATH / f"{get_current_datetime_string()}.{extension}")
