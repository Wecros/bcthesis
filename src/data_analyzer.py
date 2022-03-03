#!/usr/bin/env python3

from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import math


def main():
    data_dir = Path('../data/repaired/1000coins')
    assert data_dir.is_dir()

    # TODO: create all_coins in format [{'BTC': pathToTheBTCFile}, ...]
    all_coins = [file for file in data_dir.iterdir() if file.is_file]
    print(all_coins)

    btc_price = get_close_dataframe("../data/repaired/1000coins/BTC-bitcoin.csv")
    analyze_data("../data/repaired/1000coins/ETH-ethereum.csv", btc_price)


def get_close_dataframe(data_path: str):
    df = pd.read_csv(data_path)
    df.head()
    return df["close"]


def analyze_data(data_path: str, btc_price):
    df = pd.read_csv(data_path)
    df.head()

    df["date"] = pd.to_datetime(df["date"])

    x = np.arange(0, len(df))
    fig, ax = plt.subplots(1, figsize=(12, 6))
    # for idx, val in df.iterrows():
    # plt.plot([x[idx], x[idx]], [0, val['close']])

    print(
        "Correlation value between coin price and its market capitalization:",
        df["close"].corr(df["marketCapUSD"]),
    )
    print(
        "Correlation value between coin price and the total market cap of crypto market:",
        1,
    )
    print(
        "Correlation value between coin price and BTC price:",
        df["close"].corr(btc_price),
    )

    plt.plot(df["date"], df["close"])
    plt.show()


if __name__ == "__main__":
    main()
