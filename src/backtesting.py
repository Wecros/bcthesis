#!/usr/bin/env python3

import vectorbt as vbt
import pandas as pd
import numpy as np

def get_close_series(data_path: str):
    df = pd.read_csv(data_path)[::-1]
    df = df.set_index("date")
    return df["close"]

price = get_close_series("../data/repaired/1000coins/ETH-ethereum.csv")
days = 365 * 2
price = price.tail(days)

# pf = vbt.Portfolio.from_holding(price, init_cash=100)
# print(pf.total_profit())
# print(pf.stats())
# pf.plot().show()

fast_ma = vbt.MA.run(price, 10)
slow_ma = vbt.MA.run(price, 50)
entries = fast_ma.ma_crossed_above(slow_ma)
exits = fast_ma.ma_crossed_below(slow_ma)

pf = vbt.Portfolio.from_signals(price, entries, exits, init_cash=100)

print(pf.total_profit())
print(pf.stats())
pf.plot().show()
