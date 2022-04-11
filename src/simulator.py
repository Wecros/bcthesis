import logging

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
import vectorbt as vbt

from utils import Portfolio, Simulation, get_dates_from_index, get_symbols_from_index


def simulate(data):
    logging.info("Running simulation")

    # plot_all_coins(data)

    run_simulation_riskmetric(data)


def plot_all_coins(data):
    fig = px.line(data.reset_index(), x="open_time", y="close", color="pair", log_y=True)
    fig.show()


def run_simulation_riskmetric(data):
    # riskmetric = get_risk_metric(data)
    # plot_riskmetric(riskmetric, data)
    run_simulation(data)


def run_simulation(data: pd.DataFrame):
    portfolio = Portfolio(usd=100, coins={k: 0 for k in get_symbols_from_index(data)})
    sim = Simulation(portfolio=portfolio)
    riskmetric = get_risk_metric(data)  # would be class instance variable

    date_range = get_dates_from_index(data)
    for date in date_range:
        sim = do_simulation_step(sim, data, date, riskmetric)

    print(sim.portfolio.usd)
    print(sim.portfolio.coins)
    print(sim.portfolio.coins["BTCUSDT"] * data.loc["BTCUSDT"].iloc[-1].close)

    normalized_metric = riskmetric.avg * data.loc["BTCUSDT"]["open"]

    df = pd.DataFrame()
    df.index = get_dates_from_index(data)
    df["BTC_price"] = data.loc["BTCUSDT"].close
    df["risk_metric"] = normalized_metric
    fig = px.line(df)

    fig.add_trace(
        go.Scatter(
            x=sim.bought_dates,
            y=data.loc[("BTCUSDT", sim.bought_dates), :].close,
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
            x=sim.sold_dates,
            y=data.loc[("BTCUSDT", sim.sold_dates), :].close,
            mode="markers",
            name="sold",
            marker_symbol="triangle-down",
            marker=dict(
                color="red",
                size=15,
            ),
        ),
    )
    fig.show()


def do_simulation_step(
    sim: Simulation, data: pd.DataFrame, date: pd.Timestamp, riskmetric
):
    """Risk metric simulation step."""
    coin = "BTCUSDT"

    if riskmetric.loc[date]["avg"] >= 0.7:
        if not sim.sold_state:
            sim.sell(date)
            close = data.loc[(coin, date)]["close"]
            sim.portfolio.usd = sim.portfolio.coins[coin] * close
            sim.portfolio.coins[coin] = 0
    elif riskmetric.loc[date]["avg"] < 0.7:
        if not sim.bought_state:
            sim.buy(date)
            close = data.loc[(coin, date)]["close"]
            sim.portfolio.coins[coin] = sim.portfolio.usd / close
            sim.portfolio.usd = 0

    return sim


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
