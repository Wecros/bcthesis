"""
Author: Marek Filip 2022

File for getting dataframe data from Coinmarketcap API.

For Coinmarket API see: https://coinmarketcap.com/api/
"""

import json
import logging

import pandas as pd
import requests
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects

from .utils import (
    COINMARKETCAP_DATA_PATH,
    COINMARKETCAP_GLOBAL_METRICS_URL,
    COINMARKETCAP_LIMIT,
    SEP,
    TIME_FORMAT,
    convert_csv_to_df,
    interpolate_missing_dates,
)


def get_global_metrics_from_coinmarketcap(
    start_date: pd.Timestamp, end_date: pd.Timestamp
) -> pd.DataFrame:
    """Get global metrics in form of a Pandas data frame, including Bitcoin and Ethereum dominance,
    total market capitalization and volume and some altcoin information. CoinMarketCap API is used.
    """
    # Make start_date go historical because of riskmetric calculations
    start_date = pd.Timestamp("2013-04-29")

    # Adjust off by 1 got from API
    start_date -= pd.Timedelta(days=1)
    end_date += pd.Timedelta(days=1)

    # check if csv file does not already exist for previous data
    for file in COINMARKETCAP_DATA_PATH.iterdir():
        if does_global_metrics_file_meet_criteria(file, start_date, end_date):
            logging.info(f"opening existing csv file: {file}")
            df = convert_csv_to_df(file, "date")
            return df[start_date:end_date]

    response_json = get_response_dict_from_api(start_date, end_date)
    df = convert_global_metrics_json_to_dataframe(response_json)
    df = interpolate_missing_dates(df)

    path_to_csv = (
        f"{COINMARKETCAP_DATA_PATH}/global-metrics{SEP}"
        + f"{start_date.strftime(TIME_FORMAT)}{SEP}"
        + f"{end_date.strftime(TIME_FORMAT)}"
    )
    df.to_csv(path_to_csv, encoding="utf-8")
    logging.info(f"saving csv to: {path_to_csv}")
    return df


def does_global_metrics_file_meet_criteria(file, start_date, end_date):
    _, file_start_date, file_end_date = file.stem.split(SEP)
    [file_start_date, file_end_date] = map(pd.to_datetime, [file_start_date, file_end_date])
    if start_date >= file_start_date and end_date <= file_end_date:
        return True
    return False


def get_response_dict_from_api(start_date, end_date):
    def get_parameters(start_date, end_date):
        return {
            "format": "chart",
            "timeStart": str(int(start_date.timestamp())),
            "timeEnd": str(int(end_date.timestamp())),
            "interval": "1d",
        }

    days_between_dates = pd.Timedelta(end_date - start_date).days
    assert days_between_dates > 0

    # Take API limit into account
    params_list = []
    if days_between_dates > COINMARKETCAP_LIMIT:
        temp_start_date = start_date
        while days_between_dates > COINMARKETCAP_LIMIT:
            temp_end_date = temp_start_date + pd.Timedelta(days=COINMARKETCAP_LIMIT)
            params_list.append(get_parameters(temp_start_date, temp_end_date))
            temp_start_date = temp_end_date + pd.Timedelta(days=1)
            days_between_dates = (end_date - temp_end_date).days
        start_date = temp_start_date
    params_list.append(get_parameters(start_date, end_date))

    responses = []
    try:
        responses = list(
            requests.get(COINMARKETCAP_GLOBAL_METRICS_URL, params=params) for params in params_list
        )
    except (ConnectionError, Timeout, TooManyRedirects) as e:
        logging.error(e)

    individual_global_metrics = [json.loads(response.text) for response in responses]
    global_metrics = individual_global_metrics[0]
    for metrics in individual_global_metrics[1:]:
        global_metrics["data"]["quotes"].extend(metrics["data"]["quotes"])
    return global_metrics


def convert_global_metrics_json_to_dataframe(response: dict):
    data = response["data"]["quotes"]

    # NOTE: All marketcap data is reported in $USD
    output_data = {
        "date": [],
        "btc_dominance": [],
        "eth_dominance": [],
        "altcoin_marketcap": [],
        "altcoin_volume_24h": [],
        "total_marketcap": [],
        "total_volume_24h": [],
    }
    for entry in data:
        output_entry = {}
        output_entry["btc_dominance"] = entry["btcDominance"]
        output_entry["eth_dominance"] = entry.get("ethDominance", 0)
        output_entry["date"] = pd.Timestamp(entry["timestamp"]).tz_localize(None).normalize()

        quote = entry["quote"][0]
        output_entry["altcoin_marketcap"] = quote["altcoinMarketCap"]
        output_entry["altcoin_volume_24h"] = quote["altcoinVolume24H"]
        output_entry["total_marketcap"] = quote["totalMarketCap"]
        output_entry["total_volume_24h"] = quote["totalVolume24H"]

        for key, value in output_entry.items():
            output_data[key].append(value)

    df = pd.DataFrame.from_dict(output_data)
    df.index = df["date"]
    df = df.drop(columns=["date"])
    return df
