import argparse
from dataclasses import dataclass

import pandas as pd
import yaml

from utils import TIME_FORMAT


@dataclass
class TradingVariables:
    """Dataclass holding the trading variables influencing the simulation"""

    pairs: list
    start_date: pd.Timestamp
    end_date: pd.Timestamp
    interval: pd.Timedelta

    def get_interval_in_day_fraction(self):
        """Get interval as a fraction of number of days."""
        return self.interval.delta / pd.Timedelta(days=1).delta


@dataclass
class TradingData:
    """Dataclass holding all information needed to run the simulation."""

    data: dict  # {"BTCUSDT": pd.DataFrame, "ETHUSDT": ...}
    variables: TradingVariables


def convert_args_to_trading_variables(args):
    """Get trading variables from the input argument file in a managable dataclass."""
    variables = {"pairs": args["pairs"]}
    variables["start_date"], variables["end_date"] = map(
        pd.to_datetime, [args["start_date"], args["end_date"]]
    )
    variables["interval"] = pd.to_timedelta(args["interval"])
    return TradingVariables(**variables)


def get_parsed_args():
    """Parse the arguments either from file or the command line."""
    parser = get_parser()
    args = parser.parse_args()
    if not args.file and not (
        args.interval and args.pairs and args.start_date and args.end_date
    ):
        parser.error("Incomplete arguments or no argument file defined!")

    if args.file:
        return parse_yaml(args)
    return {
        "pairs": args.pairs,
        "start_date": args.start_date,
        "end_date": args.end_date,
        "interval": args.interval,
    }


def get_parser():
    parser = argparse.ArgumentParser(description="Download CSV from Binance API.")
    parser.add_argument(
        "-p", "--pairs", help="list of pairs seperated by a space character"
    )
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
    return parser


def parse_yaml(args):
    with open(args.file, "r") as file:
        return yaml.load(file, Loader=yaml.CLoader)