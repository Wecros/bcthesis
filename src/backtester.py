#!/usr/bin/env python3

import logging

from argparser import TradingData, convert_args_to_trading_variables, get_parsed_args
from binance_api_downloader import get_data
from simulator import run_simulation


def main():
    logging_setup()
    args = get_parsed_args()
    trading_vars = convert_args_to_trading_variables(args)

    klines_data = {}
    for pair in trading_vars.pairs:
        args = {
            "ticker": pair,
            "start_date": trading_vars.start_date,
            "end_date": trading_vars.end_date,
            "interval": args["interval"],
        }
        klines_data[pair] = get_data(args)

    data = TradingData(klines_data, trading_vars)
    for ticker, df in data.data.items():
        run_simulation(df)


def logging_setup():
    logging.basicConfig(
        level=logging.INFO,
        format="[%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[logging.FileHandler("lastrun.log", mode="w"), logging.StreamHandler()],
    )


if __name__ == "__main__":
    main()
