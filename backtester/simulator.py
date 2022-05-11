"""
File for orchestrating the various strategies in play.
"""

import logging
from copy import deepcopy

from .plotter import Plotter
from .riskmetric_calculator import RiskMetricOptimizations, get_risk_metric
from .strategy import Strategy
from .utils import (
    BTC_SYMBOL,
    TIME_FORMAT,
    Portfolio,
    StrategyResult,
    TradingData,
    create_portfolio_from_data,
    ensure_same_dates_between_dataframes,
    get_dates_from_index,
    get_historical_data_if_btc_is_only_coin_considered,
    noop,
    set_index_for_data,
)

set_index_for_data
get_historical_data_if_btc_is_only_coin_considered
ensure_same_dates_between_dataframes
get_dates_from_index


def simulate(trading_data: TradingData):
    logging.info("Running simulation")

    # trading_data = get_historical_data_if_btc_is_only_coin_considered(trading_data)

    historical_data_used = trading_data.btc_historical

    optimizations = RiskMetricOptimizations(
        diminishing_returns=False, daily_volume_correlation=False
    )
    # optimizations_dim = RiskMetricOptimizations(
    # diminishing_returns=True, daily_volume_correlation=False
    # )
    # optimizations_dim_vol = RiskMetricOptimizations(
    # diminishing_returns=True, daily_volume_correlation=True
    # )
    # optimizations_vol = RiskMetricOptimizations(
    # diminishing_returns=False, daily_volume_correlation=True
    # )

    riskmetric = get_risk_metric(
        historical_data_used, optimizations, trading_data.dates[0], trading_data.dates[-1]
    )
    # riskmetric_dim = get_risk_metric(
    # historical_data_used, optimizations_dim, trading_data.dates[0], trading_data.dates[-1]
    # )
    # riskmetric_dim_vol = get_risk_metric(
    # historical_data_used, optimizations_dim_vol, trading_data.dates[0], trading_data.dates[-1]
    # )
    # riskmetric_vol = get_risk_metric(
    # historical_data_used, optimizations_vol, trading_data.dates[0], trading_data.dates[-1]
    # )

    # riskmetric_market_cap = get_risk_metric(
    # trading_data.global_metrics, optimizations, trading_data.dates[0], trading_data.dates[-1]
    # )
    # riskmetric_dim_market_cap = get_risk_metric(
    # trading_data.global_metrics,
    # optimizations_dim,
    # trading_data.dates[0],
    # trading_data.dates[-1],
    # )
    # riskmetric_dim_vol_market_cap = get_risk_metric(
    # trading_data.global_metrics,
    # optimizations_dim_vol,
    # trading_data.dates[0],
    # trading_data.dates[-1],
    # )
    # riskmetric_vol_market_cap = get_risk_metric(
    # trading_data.global_metrics,
    # optimizations_vol,
    # trading_data.dates[0],
    # trading_data.dates[-1],
    # )

    # df = trading_data.data.reset_index()
    # df = df.set_index(['open_time'])
    # df, riskmetric_dim_vol = ensure_same_dates_between_dataframes(df, riskmetric_dim_vol)
    # df, riskmetric_dim_vol_market_cap = (
    # ensure_same_dates_between_dataframes(df, riskmetric_dim_vol_market_cap)
    # )
    # df = df.reset_index()
    # df = df.rename(columns={"index": "open_time"})
    # trading_data.data = set_index_for_data(df)
    # trading_data.dates = get_dates_from_index(trading_data.data)

    strategy_list = [
        # [ShortTermStrategyIdeal],
        # [ShortTermStrategyReal],
        # [ShortTermStrategyAdjusted, {"riskmetric": riskmetric}],
        # [HodlStrategy],
        # [RebalanceStrategy],
        # [RiskMetricStrategyRealExtrema, {"riskmetric": riskmetric}],
        # [RiskMetricStrategyRealExtrema, {"riskmetric": riskmetric_dim}],
        # [RiskMetricStrategyRealExtrema, {"riskmetric": riskmetric_market_cap}],
        # [RiskMetricStrategyRealExtrema, {"riskmetric": riskmetric_dim_market_cap}],
        # [DCAStrategy],
        # [RebalanceStrategy, {'interval': 1}],
        # [RiskMetricStrategyExtremaLogic, {'riskmetric': riskmetric_dim}],
        # [RiskMetricStrategyExtremaLogic, {'riskmetric': riskmetric_market_cap}],
        # [RiskMetricStrategyExtremaLogic, {'riskmetric': riskmetric_dim_market_cap}],
        # [DCARiskMetricStrategyFibonacciAdjusted, {"riskmetric": riskmetric}],
        # [DCARiskMetricStrategyFibonacciAdjusted, {"riskmetric": riskmetric_dim}],
        # [DCARiskMetricStrategyFibonacciAdjusted, {"riskmetric": riskmetric_dim_vol}],
        # [DCARiskMetricStrategyFibonacciAdjusted, {"riskmetric": riskmetric_dim_market_cap}],
        # [DCARiskMetricStrategyFibonacciAdjusted, {"riskmetric": riskmetric_dim_vol_market_cap}],
        # [DCAStrategy],
        # [DCARiskMetricStrategyFibonacci, {"riskmetric": riskmetric}],
        # [DCARiskMetricStrategyFibonacciAdjusted, {"riskmetric": riskmetric}],
    ]

    # portfolio = create_portfolio_from_data(trading_data, cash=0)
    portfolio = create_portfolio_from_data(
        trading_data, cash=trading_data.data.loc[(BTC_SYMBOL, trading_data.dates[0]), "close"]
    )

    simgen = StrategyGenerator(strategy_list, trading_data, portfolio)
    simgen.run()
    results = simgen.get_results()

    # results[2].name = "Extrema - no optimizations"
    # results[3].name = "Extrema + diminishing returns"
    # results[4].name = "Extrema - no optimizations | market cap"
    # results[5].name = "Extrema + dim returns | market cap"

    annotation_text = (
        f"Data Range: {trading_data.dates[0].strftime(TIME_FORMAT)}--"
        f"{trading_data.dates[-1].strftime(TIME_FORMAT)} | "
        f"Data Interval: {trading_data.variables.interval_str}"
    )
    annotation_text
    riskmetric

    plotter = Plotter(
        trading_data,
        results,
        x_title=f"{trading_data.variables.interval_str} steps",
        # y_title="Profit in $USD",
        y_title="Profits in $USD",
        # y_title="Return of investment (x times)",
        # title_text=f"Strategy Experiments ({annotation_text})",
        title_text="",
    )

    hodl_profit = (
        trading_data.data.loc[(BTC_SYMBOL, trading_data.dates[-1]), "close"]
        / trading_data.data.loc[(BTC_SYMBOL, trading_data.dates[0]), "close"]
    )
    logging.info(f"HODL strategy profit: {hodl_profit}")

    plotter.plot_all_symbols()

    # plotter.plot_riskmetric_on_second_scale(riskmetric)
    # plotter.plot_riskmetric_maxima_minima_on_second_scale(riskmetric)
    # short_strat_riskmetric = ShortTermStrategyIdeal(trading_data).riskmetric
    # plotter.plot_riskmetric_on_second_scale(
    # short_strat_riskmetric,
    # riskmetric_col="risk",
    # name="Bitcoin moving average",
    # title="Bitcoin Moving Average",
    # )

    plotter.plot_strategies()

    # plotter.plot_bought_dates()
    # plotter.plot_sold_dates()
    # plotter.plot_riskmetric_maxima_minima_on_second_scale(short_strat_riskmetric)

    # plotter.plot_log_y_first_axis()
    plotter.show()
    plotter.save("pdf")


class StrategyGenerator:
    def __init__(
        self, strategy_classes: list[list[Strategy, dict]], data: TradingData, portfolio=None
    ):
        self.base_portfolio = portfolio
        if self.base_portfolio is None:
            self.base_portfolio = create_portfolio_from_data(data)
        self.strategies = get_strategy_instances_from_classes_and_kwargs(
            strategy_classes, data, self.base_portfolio
        )

    def run(self):
        for strategy in self.strategies:
            strategy.run_simulation()
            # logging.info(f"{strategy.name}: {strategy.profits_in_time[-1]}")
            logging.info(strategy.stats())

    def get_results(self):
        results = []
        for strategy in self.strategies:
            result = StrategyResult(
                strategy.name, strategy.profits_in_time, strategy.bought_dates, strategy.sold_dates
            )
            results.append(result)
        return results


class StrategyMerger(Strategy):
    def __init__(self, data: TradingData, shared_portfolio: Portfolio = None, **kwargs):
        super().__init__(data, shared_portfolio)
        strategy_classes: list[list[Strategy, dict]] = kwargs.get("strategy_classes", [])

        self.strategies: tuple[Strategy] = get_strategy_instances_from_classes_and_kwargs(
            strategy_classes, data, None
        )
        for strategy in self.strategies:
            strategy.log_profits = noop
            strategy.portfolio = self.portfolio
        self.name = "Merged:" + "-".join(strat.name for strat in self.strategies)

    def execute_step(self):
        self.name = "Merged:" + "-".join(strat.name for strat in self.strategies)
        for strategy in self.strategies:
            ...
            strategy.current_step = self.steps[self.i]
            strategy.execute_step()
        self.profits_in_time[self.i] = self.get_profit_in_usd()


def get_strategy_instances_from_classes_and_kwargs(strategy_classes, data, portfolio):
    return tuple(
        _get_strategy_instance_from_class_and_kwargs(x, data, portfolio) for x in strategy_classes
    )


def _get_strategy_instance_from_class_and_kwargs(cls_and_kwargs, data, portfolio):
    cls: Strategy = cls_and_kwargs[0]
    kwargs: dict = {}
    if len(cls_and_kwargs) == 2:
        kwargs = cls_and_kwargs[1]

    strategy = cls(data, deepcopy(portfolio), **kwargs)
    logging.debug("- " + str(strategy))
    return strategy
