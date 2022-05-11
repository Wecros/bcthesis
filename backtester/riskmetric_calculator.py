"""
Module exposing the risk metric calculation functions.
"""

from dataclasses import dataclass

import numpy as np
import pandas as pd
from autots import AutoTS
from scipy.signal import argrelextrema

from .utils import FIRST_BITCOIN_EXCHANGE

NO_DAYS_MA = 50  # Number of days that the moving averages are calculated for
NO_DAYS_24H_VOLUME = 7  # Number of days that the daily volume is calculated for


@dataclass
class RiskMetricOptimizations:
    """Data container for the possible risk optimizations."""

    diminishing_returns: bool = False
    daily_volume_correlation: bool = False


def get_risk_metric(
    historical_data: pd.DataFrame,
    optimizations: RiskMetricOptimizations,
    start_date: pd.Timestamp,
    end_date: pd.Timestamp,
) -> pd.DataFrame:
    """Get risk metric dataframe calculated from the historical data and optimiztions data."""
    df = historical_data.copy()
    # When using total market capitalization we need to change the column name accordingly.
    if "total_marketcap" in df:
        df["price"] = df["total_marketcap"]
    # When using the Binance data we need to change the column name accordingly.
    if "close" in df:
        df["price"] = df["close"]
    riskmetric_df = _calculate_risk_metric(df, optimizations)
    return riskmetric_df[start_date:end_date]


def _calculate_risk_metric(df: pd.DataFrame, optimizations: RiskMetricOptimizations):
    # General MA risk metric
    df["MA_short"] = df["price"].rolling(NO_DAYS_MA, min_periods=1).mean().dropna()
    df["MA_long"] = df["price"].rolling(NO_DAYS_MA * 7, min_periods=1).mean().dropna()
    df["risk"] = df["MA_short"] / df["MA_long"]

    if optimizations.diminishing_returns:
        df = _calculate_dim_returns(df)

    if optimizations.daily_volume_correlation:
        df = _calculate_daily_volume_correlation(df)

    df["riskmetric"] = (df["risk"] - df["risk"].cummin()) / (
        df["risk"].cummax() - df["risk"].cummin()
    )

    checked_values_after_before = 5
    df["min"] = df.iloc[
        argrelextrema(df.riskmetric.values, np.less_equal, order=checked_values_after_before)[0]
    ]["riskmetric"]
    df["max"] = df.iloc[
        argrelextrema(df.riskmetric.values, np.greater_equal, order=checked_values_after_before)[0]
    ]["riskmetric"]
    df["min_real"] = df["min"].shift(checked_values_after_before)
    df["max_real"] = df["max"].shift(checked_values_after_before)

    df = df[["riskmetric", "price", "min", "max", "min_real", "max_real"]]
    riskmetric_df = df[df["riskmetric"].notna()]
    return riskmetric_df


def _calculate_dim_returns(df: pd.DataFrame):
    start_d = (df["MA_short"].index.values[0] - FIRST_BITCOIN_EXCHANGE).days
    end_d = (df["MA_short"].index.values[-1] - FIRST_BITCOIN_EXCHANGE).days
    d = pd.Series(range(start_d, end_d + 1))
    d.index = pd.date_range(start=df["price"].index.values[0], periods=d.size)
    df["risk"] = df["risk"] * np.log(d)
    return df


def _calculate_daily_volume_correlation(df: pd.DataFrame):
    lastdays = df["total_volume_24h"].rolling(NO_DAYS_24H_VOLUME).mean().dropna()
    lastdays = (lastdays - lastdays.cummin()) / (lastdays.cummax() - lastdays.cummin())
    df["risk"] = (df["risk"] - df["risk"].cummin()) / (df["risk"].cummax() - df["risk"].cummin())
    df["risk"] = df["risk"] + ((lastdays - 0.5) * 0.2)
    return df


def calculate_autots_prediction(
    historical_data: pd.DataFrame, start_date, end_date, forecast_length
):
    df = historical_data.copy()
    df = df[start_date:end_date]
    df = df.reset_index()

    model = AutoTS(
        forecast_length=forecast_length,
        frequency="infer",
        prediction_interval=0.9,
        ensemble=None,
        model_list="superfast",  # "superfast", "default", "fast_parallel"
        transformer_list="fast",  # "superfast",
        drop_most_recent=1,
        max_generations=4,
        num_validations=2,
        validation_method="backwards",
    )
    model = model.fit(
        df,
        date_col="date",
        value_col="price",
    )

    prediction = model.predict()

    # Print the details of the best model
    print(model)

    # point forecasts dataframe
    forecasts_df = prediction.forecast
    # upper and lower forecasts
    forecasts_up, forecasts_low = prediction.upper_forecast, prediction.lower_forecast

    # accuracy of all tried model results
    model.results()
    # and aggregated from cross validation
    model.results("validation")

    return forecasts_df, forecasts_up, forecasts_low
