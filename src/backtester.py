#!/usr/bin/env python3

import logging

import pandas as pd

from argparser import convert_args_to_trading_variables, get_parsed_args
from binance_api_downloader import get_data_from_binance
from simulator import simulate
from utils import TradingVariables, remove_distinct_dates


def main():
    logging_setup()
    args = get_parsed_args()
    trading_vars = convert_args_to_trading_variables(args)
    data = get_data(args, trading_vars)
    simulate(data)


def logging_setup():
    logging.basicConfig(
        level=logging.INFO,
        format="[%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[logging.FileHandler("lastrun.log", mode="w"), logging.StreamHandler()],
    )


def get_data(args: dict, trading_vars: TradingVariables):
    """Get data based on the information provided in the arguments."""
    pairs_dataframes = [
        get_dataframe_for_trading_pair(args, trading_vars, pair) for pair in trading_vars.pairs
    ]
    data = pd.concat(pairs_dataframes)
    data = remove_distinct_dates(data)
    return data.sort_index()


def get_dataframe_for_trading_pair(args, trading_vars: TradingVariables, pair: str):
    args = {
        "ticker": pair,
        "start_date": trading_vars.start_date,
        "end_date": trading_vars.end_date,
        "interval": args["interval"],
    }
    data = get_data_from_binance(args)

    if args["interval"] == "1d":
        # normalize the datetime to midnight if interval is 1 day
        data.index = data.index.map((lambda x: pd.Timestamp(x).replace(hour=0, minute=0, second=0)))

    multinindex = pd.MultiIndex.from_product(
        [[pair], data.index.values], names=["pair", "open_time"]
    )
    df = pd.DataFrame(
        data.values,
        columns=["open", "high", "low", "close", "volume"],
        index=multinindex,
    )
    return df


if __name__ == "__main__":
    main()
