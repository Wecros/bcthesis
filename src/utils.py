"""Utils file for defining helpful functions and constants."""

from datetime import timedelta

import pandas as pd

DATA_PATH = "../data/"
CUSTOM_DATA_PATH = "repaired/1000coins/"
BINANCE_PATH = "binance/"
SEP = ":"
TIME_FORMAT = "%Y-%m-%d"
DEBUG = True


def convert_csv_to_df(csv_file):
    df = pd.read_csv(csv_file)
    df["open_time"] = pd.to_datetime(df["open_time"])
    df = df.set_index("open_time")
    return df


def get_interval_from_df(df: pd.DataFrame):
    """Get interval in days from dataframe. This means that a 5m interval dataframe
    will return a fraction of a day
    """
    interval = df.index[1] - df.index[0]
    return interval


def interval_in_days(days: int, df: pd.DataFrame) -> int:
    """Return interval in steps in relation to the dataframe interval."""
    interval = get_interval_from_df(df)
    days_fraction = interval.total_seconds() / timedelta(days=1).total_seconds()
    return int(days / days_fraction)


def get_timedelta_as_binance_interval(delta: pd.Timedelta):
    days, hours, minutes, seconds, _, _, _ = delta.components
    if days > 7:
        return "1M"
    elif days == 7:
        return "1w"
    elif days:
        return str(days) + "d"
    elif hours:
        return str(hours) + "h"
    elif minutes:
        return str(minutes) + "m"
