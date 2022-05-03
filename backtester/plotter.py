"""
Module defining the plotter class used for plotting graphs.
"""


import numpy as np
import numpy.typing as npt
import pandas as pd
import plotly.graph_objs as go
from plotly.subplots import make_subplots

from .utils import (
    BTC_SYMBOL,
    OUTPUT_PATH,
    StrategyResult,
    TradingData,
    get_current_datetime_string,
    get_risk_metric,
    get_risk_metric_based_on_total_marketcap,
    map_values_to_specific_dates,
)

COLORBAR_CONFIG = dict(thickness=12, outlinewidth=1, dtick=0.2, tickformat=".0%")


class Plotter:
    """Plotter class.

    plot_* functions serve to customize the self.figure object.
    """

    def __init__(
        self,
        data: TradingData,
        strategy_results: list[StrategyResult],
        x_title="",
        y_title="",
        title_text="",
    ):
        # self.figure = make_subplots(*args, **kwargs)
        self.figure = go.Figure()
        self.data = data.data
        self.historical_btc = data.btc_historical
        self.global_metrics = data.global_metrics
        self.dates: npt.NDArray[pd.Timestamp] = data.dates
        self.symbols: list[str] = data.symbols
        self.strategies: list[StrategyResult] = strategy_results
        self.riskmetric = get_risk_metric(data.btc_historical, data.dates[0], data.dates[-1])

        custom_layout = go.Layout(
            template="plotly_white",
            font={
                "family": "Roboto",
                "size": 20,
                "color": "black",
            },
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.01,
                font=dict(family="Courier", size=20, color="black"),
                # bgcolor="LightSteelBlue",
                bgcolor="rgba(149, 165, 166, 0.3)",
                bordercolor="Black",
                borderwidth=2,
            ),
            showlegend=True,
            # colorway=px.colors.qualitative.Light24
        )
        self.figure.update_layout(custom_layout)
        self.change_title(title_text)
        self.figure.update_xaxes(title_text=x_title)
        self.figure.update_yaxes(title_text=y_title)

    def plot_strategies_with_data(self):
        self.plot_all_symbols()
        self.plot_strategies()

    def plot_all_symbols(self):
        for symbol in self.symbols:
            self._plot_symbol(symbol)

    def _plot_symbol(self, symbol: str):
        self.figure.add_trace(
            go.Scatter(x=self.dates, y=self.data.loc[symbol, "close"], name=symbol)
        )

    def plot_all_symbols_as_percentages(self):
        """Percentages are represented as P&L from the first value"""
        for symbol in self.symbols:
            self._plot_symbol_as_percentages(symbol)

    def _plot_symbol_as_percentages(self, symbol: str):
        df = self.data.loc[symbol]
        base = df.iloc[0]["close"]
        percentages = np.where(
            df["close"] >= base, df["close"] / base * 100 - 100, base / df["close"] * -100 + 100
        )
        self.figure.add_trace(go.Scatter(x=self.dates, y=percentages, name=symbol))

    def plot_specific_symbols(self, symbol_list):
        for symbol in symbol_list:
            self._plot_symbol(symbol)

    def plot_specific_symbols_as_percentages(self, symbol_list):
        """Percentages are represented as P&L from the first value"""
        for symbol in symbol_list:
            self._plot_symbol_as_percentages(symbol)

    def plot_strategies(self):
        for strategy in self.strategies:
            self._plot_strategy(strategy)

    def _plot_strategy(self, strategy: StrategyResult):
        self.figure.add_trace(
            go.Scatter(x=self.dates, y=strategy.profits, mode="lines", name=strategy.name)
        )

    def plot_strategies_as_percentages(self):
        """Percentages are represented as P&L from the first value"""
        for strategy in self.strategies:
            self._plot_strategy_as_percentage(strategy)

    def _plot_strategy_as_percentage(self, strategy: StrategyResult):
        base = strategy.profits[0]
        profits_percentages = np.where(
            strategy.profits >= base,
            strategy.profits / base * 100 - 100,
            base / strategy.profits * -100 + 100,
        )
        self.figure.add_trace(
            go.Scatter(x=self.dates, y=profits_percentages, mode="lines", name=strategy.name)
        )

    def plot_btc(self):
        self.figure.add_trace(
            go.Scatter(x=self.dates, y=self.data.loc[BTC_SYMBOL, "close"], name=BTC_SYMBOL)
        )

    def plot_colorcoded_riskmetric(self):
        self.figure.add_trace(
            go.Scatter(
                x=self.riskmetric.index,
                y=self.riskmetric["price"],
                mode="markers",
                marker=dict(
                    color=self.riskmetric["riskmetric"],
                    colorscale="turbo",
                    colorbar=COLORBAR_CONFIG,
                ),
                name="Colordcoded Riskmetric (BTC)",
            )
        )

    def plot_historical_btc(self):
        self.figure.add_trace(
            go.Scatter(x=self.historical_btc.index, y=self.historical_btc["price"], name="BTC-USD")
        )

    def plot_historical_btc_colorcoded_riskmetric(self):
        riskmetric = get_risk_metric(
            self.historical_btc,
            self.historical_btc.index.values[0],
            self.historical_btc.index.values[-1],
        )
        self.figure.add_trace(
            go.Scatter(
                x=riskmetric.index,
                y=riskmetric["price"],
                mode="markers",
                marker=dict(
                    color=riskmetric["riskmetric"],
                    colorscale="turbo",
                    colorbar=COLORBAR_CONFIG,
                ),
                name="Colordcoded Riskmetric (BTC)",
            )
        )

    def plot_riskmetric_on_second_scale(self):
        self.figure = make_subplots(specs=[[{"secondary_y": True}]], figure=self.figure)
        self.figure.update_yaxes(title_text="Risk Metric Scale", secondary_y=True)
        self.figure.add_trace(
            go.Scatter(
                x=self.riskmetric.index, y=self.riskmetric["riskmetric"], name="risk metric"
            ),
            secondary_y=True,
        )

    def plot_historical_btc_riskmetric_on_second_scale(self):
        riskmetric = get_risk_metric(
            self.historical_btc,
            self.historical_btc.index.values[0],
            self.historical_btc.index.values[-1],
        )
        self.figure = make_subplots(specs=[[{"secondary_y": True}]], figure=self.figure)
        self.figure.update_yaxes(title_text="Risk Metric Scale", secondary_y=True)
        self.figure.add_trace(
            go.Scatter(x=riskmetric.index, y=riskmetric["riskmetric"], name="risk metric"),
            secondary_y=True,
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

    def plot_unlog_y_first_axis(self):
        self.figure.update_layout(yaxis=dict(type="linear"))

    def plot_log_y_second_axis(self):
        self.figure.update_layout(yaxis2=dict(type="log"))

    def plot_total_market_cap(self):
        self.figure.add_trace(
            go.Scatter(
                x=self.global_metrics.index,
                y=self.global_metrics["total_marketcap"],
                name="Total crypto market cap in $USD",
            )
        )

    def plot_total_market_cap_capped_by_dates(self):
        market_cap = self.global_metrics[self.dates[0] : self.dates[-1]]
        self.figure.add_trace(
            go.Scatter(
                x=market_cap.index,
                y=market_cap["total_marketcap"],
                name="Total crypto market cap in $USD",
            )
        )

    def plot_riskmetric_colorcoded_total_market_cap(self):
        riskmetric = get_risk_metric_based_on_total_marketcap(
            self.global_metrics, self.global_metrics.index.values[0], self.dates[-1]
        )
        self.figure.add_trace(
            go.Scatter(
                x=riskmetric.index,
                y=riskmetric["price"],
                mode="markers",
                marker=dict(
                    color=riskmetric["riskmetric"],
                    colorscale="turbo",
                    colorbar=COLORBAR_CONFIG,
                ),
                name="Colordcoded Riskmetric (BTC)",
            )
        )

    def plot_riskmetric_second_scale_total_market_cap(self):
        riskmetric = get_risk_metric_based_on_total_marketcap(
            self.global_metrics, self.global_metrics.index.values[0], self.dates[-1]
        )
        self.figure = make_subplots(specs=[[{"secondary_y": True}]], figure=self.figure)
        self.figure.update_yaxes(title_text="Risk Metric Scale", secondary_y=True)
        self.figure.add_trace(
            go.Scatter(
                x=riskmetric.index, y=riskmetric["riskmetric"], name="total marketcap risk metric"
            ),
            secondary_y=True,
        )

    def show_both_log_and_linear(self):
        self.plot_unlog_y_first_axis()
        self.show()
        self.plot_log_y_first_axis()
        self.show()

    def change_title(self, title: str):
        self.figure.update_layout(
            title={
                "font": {
                    "family": "Roboto",
                    "size": 30,
                    "color": "black",
                },
                "xanchor": "center",
                "yanchor": "top",
                "y": 0.93,
                "x": 0.5,
                "text": title,
            }
        )

    def reset_traces(self):
        self.figure.data = []

    def get_figure(self):
        return self.figure

    def show(self):
        return self.figure.show()

    def save(self, extension="pdf"):
        return self.figure.write_image(OUTPUT_PATH / f"{get_current_datetime_string()}.{extension}")
