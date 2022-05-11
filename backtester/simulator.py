"""
Author: Marek Filip 2022

File for orchestrating the various strategies in play.
"""

import logging
from copy import deepcopy

from .hodl_strategy import HodlStrategy
from .plotter import Plotter
from .rebalance_strategy import RebalanceStrategy
from .riskmetric_calculator import RiskMetricOptimizations, get_risk_metric
from .riskmetric_strategy import RiskMetricStrategyRealExtrema
from .short_term_strategy import (
    ShortTermStrategyAdjusted,
    ShortTermStrategyIdeal,
    ShortTermStrategyReal,
)
from .strategy import Strategy
from .utils import (
    BTC_SYMBOL,
    Portfolio,
    StrategyResult,
    TradingData,
    create_portfolio_from_data,
    get_historical_data_if_btc_is_only_coin_considered,
    noop,
)
from .vectorbt_simulations import (
    run_simulation_vectorbt_hodl,
    run_simulation_vectorbt_msa,
)


def simulate(trading_data: TradingData):
    """The main function of the program. This is where all the simulation happens
    and results are plotted. It is called from __main__.py.
    """
    logging.info("Running simulation")

    # showcase_vectorbt(trading_data)
    showcase_coins(trading_data)
    showcase_all_metrics(trading_data)
    showcase_strategies_longterm(trading_data)
    # showcase_strategies_shortterm(trading_data)


def showcase_vectorbt(trading_data: TradingData):
    """Any portfolio can be used."""
    run_simulation_vectorbt_hodl(trading_data)
    run_simulation_vectorbt_msa(trading_data)


def showcase_coins(trading_data: TradingData):
    """Any portfolio can be used. Longer portfolio preferred. BTCUSDT preferred."""
    plotter = Plotter(
        trading_data,
        None,
        x_title=f"{trading_data.variables.interval_str} steps",
        y_title="Price in $USD",
        title_text="Showcased title",
    )
    plotter.plot_all_symbols()
    plotter.plot_diminishing_returns_expected_btc_price()

    plotter.plot_log_y()
    plotter.show()
    plotter.plot_unlog_y_first_axis()
    plotter.show()


def showcase_all_metrics(trading_data: TradingData):
    """BTCUSDT should be used. Historical data will be used instead.

    historical_data_used can be altered to switch between Bitcoin and total market
    capitalization for the metric calculation.
    """
    trading_data = get_historical_data_if_btc_is_only_coin_considered(trading_data)

    historical_data_used = trading_data.btc_historical
    # historical_data_used = trading_data.global_metrics

    optimizations = RiskMetricOptimizations(
        diminishing_returns=False, daily_volume_correlation=False
    )
    optimizations_dim = RiskMetricOptimizations(
        diminishing_returns=True, daily_volume_correlation=False
    )
    optimizations_vol = RiskMetricOptimizations(
        diminishing_returns=False, daily_volume_correlation=True
    )
    optimizations_dim_vol = RiskMetricOptimizations(
        diminishing_returns=True, daily_volume_correlation=True
    )

    riskmetric = get_risk_metric(
        historical_data_used, optimizations, trading_data.dates[0], trading_data.dates[-1]
    )
    riskmetric_dim = get_risk_metric(
        historical_data_used, optimizations_dim, trading_data.dates[0], trading_data.dates[-1]
    )
    riskmetric_vol = get_risk_metric(
        historical_data_used, optimizations_vol, trading_data.dates[0], trading_data.dates[-1]
    )
    riskmetric_dim_vol = get_risk_metric(
        historical_data_used, optimizations_dim_vol, trading_data.dates[0], trading_data.dates[-1]
    )

    plotter = Plotter(
        trading_data,
        None,
        x_title=f"{trading_data.variables.interval_str} steps",
        y_title="Price in $USD",
    )
    plotter.plot_historical_btc()
    plotter.plot_riskmetric_on_second_scale(riskmetric, name="riskmetric - no optimizations")
    plotter.plot_riskmetric_on_second_scale(riskmetric_dim, name="riskmetric + dim returns")
    plotter.plot_riskmetric_on_second_scale(riskmetric_vol, name="riskmetric + 24 vol correlation")
    plotter.plot_riskmetric_on_second_scale(
        riskmetric_dim_vol, name="riskmetric + dim returns + 24 vol corr"
    )

    plotter.plot_log_y_first_axis()
    plotter.show()


def showcase_strategies_longterm(trading_data: TradingData):
    """Portfolio of many coins can take longer to compute. 1d interval is necessary."""
    optimizations = RiskMetricOptimizations(
        diminishing_returns=False, daily_volume_correlation=False
    )
    optimizations_dim = RiskMetricOptimizations(
        diminishing_returns=True, daily_volume_correlation=False
    )
    riskmetric = get_risk_metric(
        trading_data.btc_historical, optimizations, trading_data.dates[0], trading_data.dates[-1]
    )
    riskmetric_dim = get_risk_metric(
        trading_data.btc_historical,
        optimizations_dim,
        trading_data.dates[0],
        trading_data.dates[-1],
    )

    strategy_list = [
        [HodlStrategy],
        [RebalanceStrategy],
        [RiskMetricStrategyRealExtrema, {"riskmetric": riskmetric}],
        [RiskMetricStrategyRealExtrema, {"riskmetric": riskmetric_dim}],
    ]
    portfolio = create_portfolio_from_data(
        trading_data, cash=trading_data.data.loc[(BTC_SYMBOL, trading_data.dates[0]), "close"]
    )

    simgen = StrategyGenerator(strategy_list, trading_data, portfolio)
    simgen.run()
    results = simgen.get_results()

    plotter = Plotter(
        trading_data,
        results,
        x_title=f"{trading_data.variables.interval_str} steps",
        y_title="Profits in $USD",
    )

    plotter.plot_strategies()

    plotter.plot_bought_dates()
    plotter.plot_sold_dates()

    plotter.plot_log_y_first_axis()
    plotter.show()
    plotter.save("pdf")


def showcase_strategies_shortterm(trading_data: TradingData):
    """Portfolio of 1 coin recommended, 5m interval needed."""
    strategy_list = [
        [ShortTermStrategyIdeal],
        [ShortTermStrategyReal],
        [ShortTermStrategyAdjusted],
    ]
    portfolio = create_portfolio_from_data(
        trading_data, cash=trading_data.data.loc[(BTC_SYMBOL, trading_data.dates[0]), "close"]
    )

    simgen = StrategyGenerator(strategy_list, trading_data, portfolio)
    simgen.run()
    results = simgen.get_results()

    plotter = Plotter(
        trading_data,
        results,
        x_title=f"{trading_data.variables.interval_str} steps",
        y_title="Profits in $USD",
    )
    short_strat_riskmetric = ShortTermStrategyIdeal(trading_data).riskmetric

    plotter.plot_riskmetric_on_second_scale(
        short_strat_riskmetric,
        riskmetric_col="risk",
        name="Bitcoin moving average",
        title="Bitcoin Moving Average",
    )
    plotter.plot_riskmetric_maxima_minima_on_second_scale(short_strat_riskmetric)

    plotter.plot_all_symbols()
    plotter.plot_strategies()

    plotter.plot_bought_dates()
    plotter.plot_sold_dates()

    plotter.show()
    plotter.save("pdf")


class StrategyGenerator:
    """Class used to aggregate several classes under one common interface, sharing
    the data and portfolio without having to retype it every time.
    """

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
    """Intersting strategy, which merges execute_step of multiple strategies. The order
    the strategies are defined determine the execute_step order.
    """

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
    """Get strategy instances from arguments for StrategyGenerator and StrategyMerger."""
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
