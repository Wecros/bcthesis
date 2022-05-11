"""
Author: Marek Filip 2022

File that provides common interface for all the api data.

Useful if there is a need to change the API provider,
rest of the codebase becomes unaffected by the change.
"""

from .binance_api_downloader import get_data_from_binance
from .coingecko_api_downloader import get_historical_btc_from_coingecko
from .coinmarketcap_api_downloader import get_global_metrics_from_coinmarketcap

get_historical_btc = get_historical_btc_from_coingecko
get_data = get_data_from_binance
get_global_metrics = get_global_metrics_from_coinmarketcap
