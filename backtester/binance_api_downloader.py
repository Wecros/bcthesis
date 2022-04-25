"""
File for getting dataframe data from Binance API.

for Binance API see: https://www.binance.com/en/support/faq/c-6
"""

import logging
from datetime import datetime

import numpy as np
import pandas as pd
from binance import Client
from decouple import config

from .utils import (
    BINANCE_DATA_PATH,
    SEP,
    TIME_FORMAT,
    convert_csv_to_df,
    get_dates_from_index,
)

# HACK: Line for jupyter notebook testing purposes.
# BINANCE_DATA_PATH = Path("/home/wecros/Repos/School/bcthesis/data/binance")


def get_data_from_binance(args: dict) -> pd.DataFrame:
    logging.debug(f"path to data: {BINANCE_DATA_PATH}")

    # check if csv file does not already exist for previous data
    for file in BINANCE_DATA_PATH.iterdir():
        if does_binance_file_meet_criteria(file, args):
            logging.info(f"opening existing csv file: {file}")
            df = convert_csv_to_df(file, "open_time")
            try:
                return df[args["start_date"] : args["end_date"]]
            except KeyError:
                # Binance server saves days at 02:00, so this error can happen
                return df[df.index[0] : args["end_date"]]

    client = Client(config("BINANCE_API_KEY"), config("BINANCE_SECRET_KEY"))
    klines = client.get_historical_klines(
        args["ticker"],
        args["interval"],
        args["start_date"].strftime(TIME_FORMAT),
        args["end_date"].strftime(TIME_FORMAT),
    )

    df = get_df_from_binance(klines)

    path_to_csv = (
        f"{BINANCE_DATA_PATH}/{args['ticker']}{SEP}"
        + f"{args['start_date'].strftime(TIME_FORMAT)}{SEP}"
        + f"{get_dates_from_index(df)[-1].strftime(TIME_FORMAT)}"
        + f"{SEP}{args['interval']}.csv"
    )
    df.to_csv(path_to_csv, encoding="utf-8")
    logging.info(f"saving csv to: {path_to_csv}")
    return df


def does_binance_file_meet_criteria(file, args):
    ticker, start_date, end_date, interval = file.stem.split(SEP)
    [start_date, end_date] = map(pd.to_datetime, [start_date, end_date])

    if (
        args["ticker"] == ticker
        and args["start_date"] >= start_date
        and args["end_date"] <= end_date
        and args["interval"] == interval
    ):
        return True

    return False


def get_df_from_binance(klines):
    np_klines = np.array(klines)
    df = pd.DataFrame(
        np_klines.reshape(-1, 12),
        dtype=float,
        columns=(
            "open_time",
            "open",
            "high",
            "low",
            "close",
            "volume",
            "close_time",
            "quote_asset_volume",
            "number_of_trades",
            "taker_buy_base_asset_volume",
            "taker_buy_quote_asset_volume",
            "ignore",
        ),
    )
    df = df.drop(
        columns=[
            "close_time",
            "quote_asset_volume",
            "number_of_trades",
            "taker_buy_base_asset_volume",
            "taker_buy_quote_asset_volume",
            "ignore",
        ]
    )
    df.open_time = df.open_time.apply(lambda x: datetime.fromtimestamp(x / 1000))
    df = df.set_index("open_time")
    return df
