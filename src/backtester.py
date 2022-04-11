#!/usr/bin/env python3

import logging

import pandas as pd

from argparser import convert_args_to_trading_variables, get_parsed_args
from binance_api_downloader import get_data
from simulator import run_simulation


def main():
    logging_setup()
    args = get_parsed_args()
    trading_vars = convert_args_to_trading_variables(args)

    pair_list = []
    for pair in trading_vars.pairs:
        args = {
            "ticker": pair,
            "start_date": trading_vars.start_date,
            "end_date": trading_vars.end_date,
            "interval": args["interval"],
        }

        data = get_data(args)

        if args["interval"] == "1d":
            # normalize the datetime to midnight if interval is 1 day
            data.index = data.index.map(
                (lambda x: pd.Timestamp(x).replace(hour=0, minute=0, second=0))
            )

        multinindex = pd.MultiIndex.from_product(
            [[pair], data.index.values], names=["pair", "open_time"]
        )
        df = pd.DataFrame(
            data.values,
            columns=["open", "high", "low", "close", "volume"],
            index=multinindex,
        )
        pair_list.append(df)

    data = pd.concat(pair_list)
    run_simulation(data)


def logging_setup():
    logging.basicConfig(
        level=logging.INFO,
        format="[%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[logging.FileHandler("lastrun.log", mode="w"), logging.StreamHandler()],
    )


if __name__ == "__main__":
    main()
