"""
File for getting dataframe data from Coingecko API.

For Coingecko API see: https://www.coingecko.com/en/api/documentation
"""

import logging

import pandas as pd
from pycoingecko import CoinGeckoAPI

from .utils import COINGECKO_DATA_PATH, SEP, TIME_FORMAT, convert_csv_to_df


def get_historical_btc_from_coingecko(end_date: pd.Timestamp):
    # check if csv file does not already exist for previous data
    for file in COINGECKO_DATA_PATH.iterdir():
        if does_historical_btc_file_meet_criteria(file, end_date):
            logging.info(f"opening existing csv file: {file}")
            df = convert_csv_to_df(file, "date")
            return df[:end_date]

    cg = CoinGeckoAPI()
    bitcoin_market_chart = cg.get_coin_market_chart_by_id(
        id="bitcoin", vs_currency="usd", days="max", interval="daily"
    )

    data = {}
    data["date"] = [date for date, _ in bitcoin_market_chart["prices"]]
    data["price"] = [price for _, price in bitcoin_market_chart["prices"]]
    data["total_volume"] = [volume for _, volume in bitcoin_market_chart["total_volumes"]]
    data["market_cap"] = [cap for _, cap in bitcoin_market_chart["market_caps"]]

    historical_btc = pd.DataFrame.from_dict(data)
    historical_btc["date"] = pd.to_datetime(data["date"], unit="ms").normalize()
    historical_btc.index = historical_btc["date"]
    historical_btc = historical_btc.drop(columns=["date"])

    path_to_csv = f"{COINGECKO_DATA_PATH}/btc-historical{SEP}" + f"{end_date.strftime(TIME_FORMAT)}"
    historical_btc.to_csv(path_to_csv, encoding="utf-8")
    logging.info(f"saving csv to: {path_to_csv}")
    return historical_btc


def does_historical_btc_file_meet_criteria(file, end_date: pd.Timestamp):
    _, file_end_date = file.stem.split(SEP)
    file_end_date = pd.to_datetime(file_end_date)
    if end_date <= file_end_date:
        return True
    return False
