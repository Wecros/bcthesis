"""Utils file for defining helpful functions and constants."""

from dataclasses import dataclass, field
from datetime import timedelta

import pandas as pd

DATA_PATH = "../data/"
CUSTOM_DATA_PATH = "repaired/1000coins/"
BINANCE_PATH = "binance/"
SEP = ":"
TIME_FORMAT = "%Y-%m-%d"
DEBUG = True


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


@dataclass
class Portfolio:
    """Dataclass holding all the information about current simulation portfolio."""

    usd: int = 0
    coins: dict = 0  # {'coin': percentage, 'coin': percantage}


@dataclass
class Simulation:
    """Dataclass holding all the information about the currently running sumulation."""

    portfolio: Portfolio
    signal_triggered: bool = False
    bought_state: bool = False
    sold_state: bool = True
    bought_dates: list[(pd.Timestamp, float)] = field(default_factory=list)
    sold_dates: list[(pd.Timestamp, float)] = field(default_factory=list)

    def buy(self, date):
        self.bought_dates.append(date)
        self.bought_state = True
        self.sold_state = False

    def sell(self, date):
        self.sold_dates.append(date)
        self.bought_state = False
        self.sold_state = True


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


def get_symbols_from_index(data):
    return data.index.get_level_values(level="pair").unique()


def get_dates_from_index(data):
    return data.index.get_level_values(level="open_time").unique()
