#!/usr/bin/env python3

import logging
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
from binance import Client
from decouple import config

from utils import BINANCE_PATH, DATA_PATH, TIME_FORMAT, convert_csv_to_df


def get_data(args: dict) -> pd.DataFrame:
    binance_dir = Path(DATA_PATH + BINANCE_PATH)
    for file in binance_dir.iterdir():
        if does_file_meet_criteria(file, args):
            logging.info(f"opening existing csv file: {file}")
            df = convert_csv_to_df(file)
            try:
                return df[args["start_date"] : args["end_date"]]
            except KeyError:
                # Binance server saves days at 02:00, so this error can happen
                return df[df.index[0] : args["end_date"]]

    # TODO: Custom data validation (from supervisor)
    # custom_dir = Path(DATA_PATH + CUSTOM_DATA_PATH)
    # for file in custom_dir.iterdir():
    # if does_file_meet_criteria(file, args):
    # print(file)
    # return file

    client = Client(config("BINANCE_API_KEY"), config("BINANCE_SECRET_KEY"))
    klines = client.get_historical_klines(
        args["ticker"],
        args["interval"],
        args["start_date"].strftime(TIME_FORMAT),
        args["end_date"].strftime(TIME_FORMAT),
    )

    path_to_csv = f"{DATA_PATH}{BINANCE_PATH}/{args['ticker']}:"
    f"{args['start_date'].strftime(TIME_FORMAT)}:{args['end_date'].strftime(TIME_FORMAT)}"
    f":{args['interval']}.csv"

    df = get_df_from_binance(klines)
    df.to_csv(path_to_csv, encoding="utf-8")
    logging.info(f"saving csv to: {path_to_csv}")
    return df


def does_file_meet_criteria(file, args):
    ticker, start_date, end_date, interval = file.stem.split(":")
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
