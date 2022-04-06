import logging

import numpy as np
import pandas as pd
import vectorbt as vbt

from utils import interval_in_days


def run_simulation(data):
    logging.info("Running simulation")
    # run_simlulation_hodl(data)
    # run_simulation_default_msa(data)
    run_simulation_riskmetric(data)


def run_simlulation_hodl(data):
    price = data.close
    pf = vbt.Portfolio.from_holding(price, init_cash=100)
    print(pf.total_profit())
    pf.plot().show()


def run_simulation_riskmetric(data):
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
    df.apply(pd.to_datetime, axis=0)
    print(df.tail())
    print(data.index[0])
    print(df[data.index[0] : data.index[-1]])


def get_risk_metric():
    df = pd.read_csv("btc.csv", index_col=0)
    return df


def run_simulation_default_msa(data):
    price = data.close

    fast_ma = vbt.MA.run(price, interval_in_days(10, data))
    slow_ma = vbt.MA.run(price, interval_in_days(100, data))
    entries = fast_ma.ma_crossed_above(slow_ma)
    exits = fast_ma.ma_crossed_below(slow_ma)

    pf = vbt.Portfolio.from_signals(price, entries, exits, init_cash=100)

    print(pf.total_profit())
    print(pf.stats())
    pf.plot().show()
