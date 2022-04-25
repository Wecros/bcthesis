#!/usr/bin/env python3

import logging

from .argparser import get_trading_data_from_args
from .simulator import simulate
from .utils import (
    BINANCE_DATA_PATH,
    COINGECKO_DATA_PATH,
    COINMARKETCAP_DATA_PATH,
    DATA_PATH,
    LOGS_PATH,
    OUTPUT_PATH,
    get_current_datetime_string,
)

for path in {
    LOGS_PATH,
    OUTPUT_PATH,
    DATA_PATH,
    BINANCE_DATA_PATH,
    COINMARKETCAP_DATA_PATH,
    COINGECKO_DATA_PATH,
}:
    path.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    format="[%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler(
            LOGS_PATH / f"backtester-{get_current_datetime_string()}.log", mode="w"
        ),
        logging.StreamHandler(),
    ],
)

trading_data = get_trading_data_from_args()
simulate(trading_data)
