import logging

import pandas as pd
import vectorbt as vbt

from utils import interval_in_days


def run_simulation(data: pd.DataFrame):
    logging.info("Running simulation")
    run_simlulation_hodl(data)
    # run_simulation_default_msa(data)


def run_simlulation_hodl(data: pd.DataFrame):
    price = data.close
    pf = vbt.Portfolio.from_holding(price, init_cash=100)
    print(pf.total_profit())
    pf.plot().show()


def run_simulation_default_msa(data: pd.DataFrame):
    price = data.close

    fast_ma = vbt.MA.run(price, interval_in_days(10, data))
    slow_ma = vbt.MA.run(price, interval_in_days(100, data))
    entries = fast_ma.ma_crossed_above(slow_ma)
    exits = fast_ma.ma_crossed_below(slow_ma)

    pf = vbt.Portfolio.from_signals(price, entries, exits, init_cash=100)

    print(pf.total_profit())
    print(pf.stats())
    pf.plot().show()
