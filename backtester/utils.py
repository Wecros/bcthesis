"""
Author: Marek Filip 2022

Utils file for defining auxiliary structures, functions, and constants.
"""

import logging
import sys
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from functools import reduce
from pathlib import Path

import numpy as np
import numpy.typing as npt
import pandas as pd
from schema import Optional, Or, Schema

# Constants specifying the path to certain directories
ROOT_PATH = Path(sys.argv[0]).parents[1]
DATA_PATH = ROOT_PATH / "data"
BINANCE_DATA_PATH = DATA_PATH / "binance"
COINMARKETCAP_DATA_PATH = DATA_PATH / "coinmarketcap"
COINGECKO_DATA_PATH = DATA_PATH / "coingecko"
LOGS_PATH = ROOT_PATH / "logs"
OUTPUT_PATH = ROOT_PATH / "output"
BACKTESTER_PATH = ROOT_PATH / "backtester"

COINMARKETCAP_GLOBAL_METRICS_URL = (
    "https://api.coinmarketcap.com/data-api/v3/global-metrics/quotes/historical"
)
COINMARKETCAP_LIMIT = 2000
SEP = ":"
TIME_FORMAT = "%Y-%m-%d"
BTC_SYMBOL = "BTCUSDT"
FIRST_BITCOIN_EXCHANGE = pd.Timestamp("2009-01-12")

# YAML schema defining the args.yaml file
YAML_FILE_SCHEMA = Schema(
    {
        "pairs": [str],
        "start_date": lambda date: pd.Timestamp(date),
        "end_date": lambda date: pd.Timestamp(date),
        "interval": str,
        Optional("debug_level"): Schema(Or("WARNING", "DEBUG", "INFO", "ERROR", "CRITICAL")),
    }
)


def noop(*args, **kwargs):
    """No operation function. Used for optimization purposes in StrategyMerger."""


@dataclass
class TradingVariables:
    """Dataclass holding the trading variables influencing the simulation"""

    pairs: list
    start_date: pd.Timestamp
    end_date: pd.Timestamp
    interval: pd.Timedelta
    interval_str: str

    def get_interval_in_day_fraction(self):
        """Get interval as a fraction of number of days."""
        return self.interval.delta / pd.Timedelta(days=1).delta


@dataclass
class TradingData:
    """Dataclass holding all information needed to run the simulation."""

    data: pd.DataFrame
    global_metrics: pd.DataFrame
    btc_historical: pd.DataFrame
    symbols: list[str]
    dates: npt.NDArray[pd.Timestamp]
    variables: TradingVariables


@dataclass
class Portfolio:
    """Dataclass holding all the information about current simulation portfolio."""

    usd: int = 1000
    coins: dict = field(default_factory=dict)  # {'coin': percentage, 'coin': percantage}


@dataclass
class StrategyResult:
    """Dataclass holding the strategie's result."""

    name: str
    profits: npt.NDArray[float]
    bought_dates: list[pd.Timestamp]
    sold_dates: list[pd.Timestamp]


def convert_args_to_trading_variables(args):
    """Get trading variables from the input argument file in a managable dataclass."""
    variables = {}
    variables["pairs"] = args["pairs"]
    variables["start_date"], variables["end_date"] = map(
        pd.to_datetime, [args["start_date"], args["end_date"]]
    )
    variables["interval"] = pd.to_timedelta(args["interval"])
    variables["interval_str"] = args["interval"]
    return TradingVariables(**variables)


def convert_data_to_trading_data(
    data: pd.DataFrame,
    global_metrics: pd.DataFrame,
    btc_historical: pd.DataFrame,
    trading_vars: TradingVariables,
):
    """Convert the data frame together with other variables to TradingData object."""
    symbols = trading_vars.pairs
    dates = get_dates_from_index(data)
    return TradingData(data, global_metrics, btc_historical, symbols, dates, trading_vars)


def convert_csv_to_df(csv_file, time_index_str):
    """Read CSV and convert to correct data frame format."""
    df = pd.read_csv(csv_file)
    df[time_index_str] = pd.to_datetime(df[time_index_str])
    df = df.set_index(time_index_str)
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


def get_symbols_from_index(data) -> set:
    return set(data.index.get_level_values(level="pair").unique())


def get_dates_from_index(data):
    return data.index.get_level_values(level="open_time").unique()


def map_values_to_specific_dates(all_dates, specific_dates, values):
    date_indices = map(lambda x: list(all_dates).index(x), specific_dates)
    specific_values = list(map(lambda x: values[x], date_indices))
    return specific_values


def remove_distinct_dates(data: pd.DataFrame):
    """Remove dates that do not intersect among every coin from the data frame data."""
    coins = get_symbols_from_index(data)
    for coin in coins:
        logging.info(f"{coin}: {data.loc[coin].reset_index().iloc[0]['open_time']}")

    dates = []
    for coin in set(data.index.get_level_values(level="pair")):
        dates.append(data.loc[coin].index.values)
    dates = reduce(np.intersect1d, dates)

    df = data.reset_index()
    date_filter = (df["open_time"] < dates[0]) | (df["open_time"] > dates[-1])
    df = df.drop(df.index[date_filter])
    df = set_index_for_data(df)
    return df


def set_index_for_data(data: pd.DataFrame):
    """Set the default 2-level index for the data frame data."""
    return data.set_index(["pair", "open_time"]).sort_index()


def create_portfolio_from_data(data: TradingData, cash: float = 10000):
    """Create portfolio for usd and coins. Cash parameter is used to denote dollar capital."""
    return Portfolio(usd=cash, coins={coin: 0 for coin in data.symbols})


def get_current_datetime_string():
    return f"{datetime.now().date()}:{datetime.now().time()}"


def interpolate_missing_dates(df: pd.DataFrame):
    """Interpolate missing dates - fill in the blanks with average information between
    the previous date and the next known date.
    """
    df = df.resample("D").mean()
    df = df.interpolate()
    return df


def ensure_same_dates_between_dataframes(df1, df2):
    intersect_dates = df1.index.intersection(df2.index)
    df1 = df1.loc[intersect_dates]
    df2 = df2.loc[intersect_dates]
    return df1, df2


def transform_historical_btc_to_trading_data(historical_btc: pd.DataFrame, start_date):
    """Transform price of historical bitcoin to be used as trading data in Binance format."""
    df = historical_btc.drop(columns=["market_cap"]).reset_index()
    df = df.rename(columns={"price": "close", "date": "open_time", "total_volume_24h": "volume"})
    df["pair"] = BTC_SYMBOL
    df["high"] = 0
    df["open"] = 0
    df["low"] = 0
    df = df[df["open_time"] >= start_date]
    df = set_index_for_data(df)
    df = df[["open", "high", "low", "close", "volume"]]
    return df


def get_historical_data_if_btc_is_only_coin_considered(trading_data):
    """If Bitcoin is the only coin considered and 1 day data us used,
    use historical data instead.
    """
    if trading_data.symbols == [BTC_SYMBOL] and trading_data.variables.interval_str == "1d":
        start_date = "2014-01-01"  # First total volume recorded on CoinGecko
        trading_data.data = transform_historical_btc_to_trading_data(
            trading_data.btc_historical, start_date
        )
        trading_data.dates = get_dates_from_index(trading_data.data)
    return trading_data
