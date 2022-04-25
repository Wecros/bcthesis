"""
Module responsible for getting the trading data from supplied program arguments.
"""

import argparse
import logging
import sys

import pandas as pd
import yaml
from schema import SchemaError

from .api_downloader import get_data, get_global_metrics, get_historical_btc
from .utils import (
    TIME_FORMAT,
    YAML_FILE_SCHEMA,
    TradingVariables,
    convert_args_to_trading_variables,
    convert_data_to_trading_data,
    get_dates_from_index,
    remove_distinct_dates,
)


def get_trading_data_from_args():
    """Get trading data ready for simulation."""
    args = get_parsed_args()
    trading_vars = convert_args_to_trading_variables(args)
    data_df = get_data_dataframe(trading_vars)

    # update trading variables start_date, end_date to match the data dataframe
    dates = get_dates_from_index(data_df)
    trading_vars.start_date = dates[0]
    trading_vars.end_date = dates[-1]

    global_metrics_df = get_global_metrics(trading_vars.start_date, trading_vars.end_date)
    historical_btc_df = get_historical_btc(trading_vars.end_date)
    trading_data = convert_data_to_trading_data(
        data_df, global_metrics_df, historical_btc_df, trading_vars
    )
    return trading_data


def get_parsed_args():
    """Parse the arguments either from file or the command line.

    Also update logging level based on arguments.
    """
    parser = get_argument_parser()
    args = parser.parse_args()
    if not args.file and not (args.interval and args.pairs and args.start_date and args.end_date):
        parser.error("Incomplete arguments or no argument file defined!")

    set_logging_level(args)

    if args.file:
        return parse_yaml(args)
    return {
        "pairs": args.pairs,
        "start_date": args.start_date,
        "end_date": args.end_date,
        "interval": args.interval,
    }


def get_argument_parser():
    parser = argparse.ArgumentParser(description="Download CSV from Binance API.")
    parser.add_argument("-p", "--pairs", help="list of pairs seperated by a space character")
    parser.add_argument(
        "-s",
        "--start-date",
        help=f"start date of data specified in UTC, expected format is {TIME_FORMAT}"
        "- 2022-04-30".replace(r"%", r"%%"),
    )
    parser.add_argument(
        "-e",
        "--end-date",
        help=f"end date of data specified in UTC, expected format is {TIME_FORMAT}"
        "- 2022-04-30".replace(r"%", r"%%"),
    )
    parser.add_argument("-i", "--interval", help="time interval between each ticks")
    parser.add_argument("-f", "--file", help="parse arguments from a YAML file")
    parser.add_argument(
        "-d",
        "--debug-level",
        help="Set debug level for logging",
        choices={"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"},
        default="INFO",
    )
    return parser


def set_logging_level(args):
    logging.getLogger().setLevel(getattr(logging, args.debug_level))


def parse_yaml(args):
    with open(args.file, "r") as file:
        yaml_args = yaml.load(file, Loader=yaml.CLoader)
        try:
            YAML_FILE_SCHEMA.validate(yaml_args)
        except SchemaError as se:
            logging.error(f"{args.file} configuration file does not conform to the schema. {se}")
            sys.exit(1)

        return yaml_args


def get_data_dataframe(trading_vars: TradingVariables):
    """Get data based on the information provided in the arguments."""
    pairs_dataframes = [
        get_dataframe_for_trading_pair(trading_vars, pair) for pair in trading_vars.pairs
    ]
    data = pd.concat(pairs_dataframes)
    data = remove_distinct_dates(data)
    return data.sort_index()


def get_dataframe_for_trading_pair(trading_vars: TradingVariables, pair: str):
    args = {
        "ticker": pair,
        "start_date": trading_vars.start_date,
        "end_date": trading_vars.end_date,
        "interval": trading_vars.interval_str,
    }
    data = get_data(args)

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
