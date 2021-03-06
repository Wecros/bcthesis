"""
Author: Marek Filip 2022

Module defining the plotter class used for plotting graphs.
"""

import logging

import numpy as np
import numpy.typing as npt
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
from plotly.subplots import make_subplots

from .riskmetric_calculator import calculate_autots_prediction
from .utils import (
    BTC_SYMBOL,
    FIRST_BITCOIN_EXCHANGE,
    OUTPUT_PATH,
    StrategyResult,
    TradingData,
    get_current_datetime_string,
    map_values_to_specific_dates,
)


class Plotter:
    """Plotter class that primarily serves to plot coin prices, strategy profits and
    changing risk metrics.

    Class takes list of strategy results and trading data as its input. Further titles
    can be specified.

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
        self.figure = go.Figure()
        self.data = data.data
        self.historical_btc = data.btc_historical
        self.global_metrics = data.global_metrics
        self.dates: npt.NDArray[pd.Timestamp] = data.dates
        self.symbols: list[str] = data.symbols
        self.strategies: list[StrategyResult] = strategy_results

        self.reupdate_layout()
        self.change_title(title_text)
        self.figure.update_xaxes(title_text=x_title)
        self.figure.update_yaxes(title_text=y_title)

    def plot_line(self, x, y, name):
        """Plot a simple line specifying the x and y values, and the name."""
        self.figure.add_trace(go.Scatter(x=x, y=y, mode="lines", name=name))

    def plot_strategies_with_data(self):
        """Plot both strategies and data."""
        self.plot_all_symbols()
        self.plot_strategies()

    def plot_all_symbols(self, visible=True):
        """Plot all cryptocurrency prices of the portfolio."""
        for symbol in self.symbols:
            self._plot_symbol(symbol, visible=visible)

    def _plot_symbol(self, symbol: str, visible=True):
        self.figure.add_trace(
            go.Scatter(x=self.dates, y=self.data.loc[symbol, "close"], name=symbol, visible=visible)
        )

    def plot_all_symbols_as_percentages(self):
        """Percentages are represented as P&L from the first value."""
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
        """Prices of cryptocurrency symbols defined in the symbol_list are plotted."""
        for symbol in symbol_list:
            self._plot_symbol(symbol)

    def plot_specific_symbols_as_percentages(self, symbol_list):
        """Percentages are represented as P&L from the first value"""
        for symbol in symbol_list:
            self._plot_symbol_as_percentages(symbol)

    def plot_strategies(self):
        """Plot results of all strategies in time."""
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
        """Specifically plot Bitcoin."""
        self.figure.add_trace(
            go.Scatter(x=self.dates, y=self.data.loc[BTC_SYMBOL, "close"], name=BTC_SYMBOL)
        )

    def plot_historical_btc(self):
        """Plot the historic price of Bitcoin dating to 2013."""
        self.figure.add_trace(
            go.Scatter(x=self.historical_btc.index, y=self.historical_btc["price"], name="BTC-USD")
        )

    def plot_colorcoded_riskmetric(self, riskmetric, name="Colordcoded Riskmetric (BTC)"):
        """Plot riskmetric given as input in colorcoded way."""
        COLORBAR_CONFIG = dict(thickness=12, outlinewidth=1, dtick=0.2, tickformat=".0%")
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

    def plot_riskmetric_on_second_scale(
        self,
        riskmetric,
        name="risk metric",
        dash=False,
        title="Risk Metric Scale",
        riskmetric_col="riskmetric",
        *args,
        **kwargs,
    ):
        """Plot given risk metric on the second y scale. Other arguments can be used to
        alter the look of the metric and its titles.
        """
        self.figure = make_subplots(specs=[[{"secondary_y": True}]], figure=self.figure)
        self.figure.update_yaxes(title_text=title, secondary_y=True)
        if dash:
            self.figure.add_trace(
                go.Scatter(
                    x=riskmetric.index,
                    y=riskmetric[riskmetric_col],
                    name=name,
                    line_dash="dash",
                    **kwargs,
                ),
                secondary_y=True,
            )
        else:
            self.figure.add_trace(
                go.Scatter(x=riskmetric.index, y=riskmetric[riskmetric_col], name=name, **kwargs),
                secondary_y=True,
            )

    def plot_riskmetric_maxima_minima(self, riskmetric):
        """Local minima and maxima of the given metric are plotted on the metric's risk values."""
        self.figure.add_trace(self._min_scatter(riskmetric))
        self.figure.add_trace(self._max_scatter(riskmetric))

    def plot_riskmetric_maxima_minima_on_second_scale(self, riskmetric):
        """Local minima and maxima of the given metric are plotted on the metric's risk values.

        Secondary y scale is used for the results.
        """
        self.figure.add_trace(self._min_scatter(riskmetric), secondary_y=True)
        self.figure.add_trace(self._max_scatter(riskmetric), secondary_y=True)

    def _min_scatter(self, riskmetric):
        return go.Scatter(
            x=self.dates,
            y=riskmetric["min_plot"],
            mode="markers",
            name="local min",
            marker=dict(size=10, color="blue"),
        )

    def _max_scatter(self, riskmetric):
        return go.Scatter(
            x=self.dates,
            y=riskmetric["max_plot"],
            mode="markers",
            name="local max",
            marker=dict(size=10, color="red"),
        )

    def plot_total_market_cap(self):
        self.figure.add_trace(
            go.Scatter(
                x=self.global_metrics.index,
                y=self.global_metrics["total_marketcap"],
                name="Total crypto market cap in $USD",
            )
        )

    def plot_trading_volume(self, second_scale=False):
        """Daily traded volume is plottd from the historical price of Bitcoin."""
        if second_scale:
            self.figure = make_subplots(specs=[[{"secondary_y": True}]], figure=self.figure)
            self.figure.update_yaxes(title_text="Trading Volume", secondary_y=True)

        df = self.historical_btc[self.dates[0] :].copy()

        if second_scale:
            self.figure.add_trace(
                go.Scatter(
                    x=df.index, y=df["total_volume_24h"], mode="lines", name="BTCUSDT 24h volume"
                ),
                secondary_y=True,
            )
        else:
            self.figure.add_trace(
                go.Scatter(
                    x=df.index, y=df["total_volume_24h"], mode="lines", name="BTCUSDT 24h volume"
                )
            )

    def plot_linearfit_trad_vol(self):
        df = self.historical_btc[self.dates[0] :].copy()
        df["BTC Price in $USD"] = df["price"]
        df["Daily traded volume in $USD"] = df["total_volume_24h"]
        logging.info(
            f'btc price to 24h volume correlation: {df["price"].corr(df["total_volume_24h"])}'
        )
        self.figure = px.scatter(
            df, x="BTC Price in $USD", y="Daily traded volume in $USD", trendline="ols"
        )
        self.reupdate_layout()

    def plot_autots_prediction(self, data_to_use, forecast_length=21):
        """Compute and plot the AutoTS machine-learned prediction of price data."""
        forecast_length = forecast_length
        forecast, up, low = calculate_autots_prediction(
            data_to_use,
            self.dates[0],
            self.dates[-1] - pd.Timedelta(days=forecast_length),
            forecast_length,
        )

        self.figure.add_trace(
            go.Scatter(x=forecast.index, y=forecast.price, name="AutoTS forecast"),
        )

    def plot_horizontal_line(self, value, *args, **kwargs):
        self.figure.add_hline(y=value, *args, **kwargs)

    def plot_vertical_line(self, value, *args, **kwargs):
        self.figure.add_vline(x=value, *args, **kwargs)

    def plot_bought_dates(self, strategies=None, dash=False):
        """Take the dates of strategies' buy orders and plot them using green triangle.

        dash argument can be used to plot dashed horizontal line that can be helpful
        in some use cases for visualizing, when the order happened in relation to some metric.
        """
        if strategies is None:
            strategies = self.strategies

        dates = []
        profits = []
        for strategy in strategies:
            profits_bought = map_values_to_specific_dates(
                self.dates, strategy.bought_dates, strategy.profits
            )
            dates.append(strategy.bought_dates)
            profits.append(profits_bought)

        x = np.array([date for sublist in dates for date in sublist])
        y = np.array([profit for sublist in profits for profit in sublist])

        self.figure.add_trace(
            go.Scatter(
                x=x,
                y=y,
                mode="markers",
                name="bought",
                marker_symbol="triangle-up",
                marker=dict(
                    color="green",
                    size=15,
                ),
            ),
        )
        if dash:
            for date in strategy.bought_dates:
                self.figure.add_vline(x=date, line_width=1, line_dash="dash", line_color="green")

    def plot_sold_dates(self, strategies=None, dash=False):
        """Take the dates of strategies' sell orders and plot them using red triangle.

        dash argument can be used to plot dashed horizontal line that can be helpful
        in some use cases for visualizing, when the order happened in relation to some metric.
        """
        if strategies is None:
            strategies = self.strategies

        dates = []
        profits = []
        for strategy in self.strategies:
            profits_sold = map_values_to_specific_dates(
                self.dates, strategy.sold_dates, strategy.profits
            )
            dates.append(strategy.sold_dates)
            profits.append(profits_sold)

        x = np.array([date for sublist in dates for date in sublist])
        y = np.array([profit for sublist in profits for profit in sublist])

        self.figure.add_trace(
            go.Scatter(
                x=x,
                y=y,
                mode="markers",
                name="sold",
                marker_symbol="triangle-down",
                marker=dict(
                    color="red",
                    size=15,
                ),
            ),
        )
        if dash:
            for date in strategy.sold_dates:
                self.figure.add_vline(x=date, line_width=1, line_dash="dash", line_color="red")

    def plot_diminishing_returns_expected_btc_price(self):
        """Days for diminishing returns are counted from the first transaction
        recorded in Jan 12 2009.
        """
        a = -17.01593313
        b = 5.84509376
        start_d = (self.dates[0] - FIRST_BITCOIN_EXCHANGE).days
        end_d = (self.dates[-1] - FIRST_BITCOIN_EXCHANGE).days
        d = pd.Series(range(start_d, end_d))

        price = 10 ** (a + b * np.log10(d))

        self.figure.add_trace(
            go.Scatter(
                x=self.dates,
                y=price,
                mode="lines",
                name="expected price of BTC according to formula",
            )
        )

    def show_both_log_and_linear(self):
        self.plot_unlog_y_first_axis()
        self.show()
        self.plot_log_y_first_axis()
        self.show()

    def plot_log_y(self):
        """Make all y axes a logarithmic scale."""
        self.figure.update_yaxes(type="log")

    def plot_log_y_first_axis(self):
        """Make the first y axis a logarithmic scale."""
        self.figure.update_layout(yaxis=dict(type="log"))

    def plot_unlog_y_first_axis(self):
        """Make the first y axis a linear scale."""
        self.figure.update_layout(yaxis=dict(type="linear"))

    def plot_log_y_second_axis(self):
        """Make the second y axis a logarithmic scale."""
        self.figure.update_layout(yaxis2=dict(type="log"))

    def plot_total_market_cap_capped_by_dates(self):
        """Plot the total market capitalization got from global metrics capped by the
        Plotter's trading data dates input.
        """
        market_cap = self.global_metrics[self.dates[0] : self.dates[-1]]
        self.figure.add_trace(
            go.Scatter(
                x=market_cap.index,
                y=market_cap["total_marketcap"],
                name="Total crypto market cap in $USD",
            )
        )

    def change_title(self, title: str):
        """Dynamically change the title's name."""
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

    def reupdate_layout(self):
        """Redefine the needed layout, should it be needed for a situation.

        e.g. in plot_linearfit_trad_vol()
        """
        custom_layout = go.Layout(
            template="plotly_white",
            font={
                "family": "Roboto",
                "size": 24,
                "color": "black",
            },
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.01,
                font=dict(family="Courier", size=20, color="black"),
                bgcolor="rgba(149, 165, 166, 0.3)",
                bordercolor="Black",
                borderwidth=2,
            ),
            showlegend=True,
            # 2:1 graph resolution
            width=1800,
            height=900,
            # colorway=px.colors.qualitative.Light24
        )
        self.figure.update_layout(custom_layout)

    def reset_traces(self):
        """Reset all data of the figure."""
        self.figure.data = []

    def get_figure(self):
        """Reset the object representaiton of the figure."""
        return self.figure

    def show(self):
        """Show the figure in a localhost web environment."""
        return self.figure.show()

    def save(self, extension="pdf"):
        """Save the figure into the output folder, pdf extension is chosen by default."""
        # HACK: plotly shenenigans: https://github.com/plotly/plotly.py/issues/3469
        import time

        time.sleep(1)

        filename = get_current_datetime_string()
        return self.figure.write_image(OUTPUT_PATH / f"{filename}.{extension}")
