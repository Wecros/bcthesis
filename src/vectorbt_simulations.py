"""
File that contains sample vectorbt strategies.
"""

import vectorbt as vbt

from utils import get_symbols_from_index


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
