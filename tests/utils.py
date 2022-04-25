"""
File cointaining useful functions for testing strategies.
"""

import pandas as pd

from backtester.argparser import get_data_dataframe
from backtester.utils import (
    TradingVariables,
    convert_data_to_trading_data,
    set_index_for_data,
)


def get_real_data(start_date: str, end_date: str, interval: str, symbols: list[str]):
    trading_vars = TradingVariables(
        pairs=symbols,
        start_date=[pd.Timestamp(start_date)],
        end_date=[pd.Timestamp(end_date)],
        interval=[pd.Timedelta(interval)],
        interval_str=interval,
    )
    data = get_data_dataframe(trading_vars)
    return data


def get_data_from_dict(start_date: str, end_date: str, interval: str, symbols: set[str]):
    dates = pd.date_range(start_date, end_date, freq=interval)

    trading_vars = TradingVariables(
        pairs=symbols,
        start_date=dates[0],
        end_date=dates[-1],
        interval=pd.Timedelta(interval),
        interval_str=interval,
    )

    data_dict = {
        "pair": [],
        "open_time": [],
        "open": [],
        "high": [],
        "low": [],
        "close": [],
        "volume": [],
    }
    for symbol in symbols:
        data_dict = _add_symbol_to_dict_data(data_dict, symbol, dates)
    df = pd.DataFrame.from_dict(data_dict)
    df = set_index_for_data(df)
    data = convert_data_to_trading_data(df, None, None, trading_vars)
    return data


def _add_symbol_to_dict_data(
    data, symbol, dates, open=None, high=None, low=None, close=None, volume=None
):
    new_data = data.copy()
    new_data["pair"].extend([symbol for date in dates])
    new_data["open_time"].extend(dates)

    arguments = {
        k: v for k, v in locals().items() if k in ["open", "high", "low", "close", "volume"]
    }
    for arg, value in arguments.items():
        if value is None:
            value = [0 for date in dates]
        new_data[arg].extend(value)
    return new_data
