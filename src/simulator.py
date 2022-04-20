import logging

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
import vectorbt as vbt
from plotly.subplots import make_subplots

from riskmetric_strategy import RiskMetricStrategy
from utils import get_dates_from_index, get_symbols_from_index


def simulate(data):
    logging.info("Running simulation")

    # plot_all_coins(data)

    strategy = RiskMetricStrategy(data)
    strategy.run_strategy()
    print(strategy.stats())
    # strategy.plot().show()

    plot_strategies(data, [strategy]).show()


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


def plot_riskmetric(riskmetric, data):
    normalized_metric = riskmetric.avg * max(data.open)
    df = pd.DataFrame()
    df.index = riskmetric.index
    df["BTC_price"] = data.loc["BTCUSDT"].open
    df["risk_metric"] = normalized_metric
    fig = px.line(df)
    fig.show()


def run_simulation_vectorbt_hodl(data):
    for symbol in get_symbols_from_index(data):
        df = data.loc[symbol]
        price = df.close
        pf = vbt.Portfolio.from_holding(price, init_cash=100)
        print(pf.total_profit())
        pf.plot().show()


def run_simulation_vectorbt_msa(data):
    for symbol in get_symbols_from_index(data):
        df = data.loc[symbol]
        price = df.close

        fast_ma = vbt.MA.run(price, 10)
        slow_ma = vbt.MA.run(price, 100)
        entries = fast_ma.ma_crossed_above(slow_ma)
        exits = fast_ma.ma_crossed_below(slow_ma)

        pf = vbt.Portfolio.from_signals(price, entries, exits, init_cash=100)
        print(pf.total_profit())
        # print(pf.stats())
        pf.plot().show()
