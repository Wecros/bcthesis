"""
File for orchestrating the various strategies in play.
"""

import logging
from copy import deepcopy

from .dca_strategy import DCAStrategy
from .hodl_strategy import HodlStrategy
from .plotter import Plotter
from .rebalance_strategy import RebalanceStrategy
from .riskmetric_calculator import RiskMetricOptimizations, get_risk_metric
from .riskmetric_strategy import RiskMetricStrategy
from .strategy import Strategy
from .utils import (
    TIME_FORMAT,
    Portfolio,
    StrategyResult,
    TradingData,
    create_portfolio_from_data,
    noop,
)

# HACK: Imports will not be removed automatically by formatter.
HodlStrategy
RebalanceStrategy
RiskMetricStrategy
DCAStrategy


def simulate(trading_data: TradingData):
    logging.info("Running simulation")

    # trading_data = get_historical_data_if_btc_is_only_coin_considered(trading_data)

    optimizations = RiskMetricOptimizations(
        diminishing_returns=False, daily_volume_correlation=True
    )
    riskmetric = get_risk_metric(
        trading_data.global_metrics, optimizations, trading_data.dates[0], trading_data.dates[-1]
    )

    strategy_list = [
        [HodlStrategy],
        [RiskMetricStrategy, {"riskmetric": riskmetric}],
        # [RebalanceStrategy],
        # [RebalanceStrategy, {"rebalance_interval": 5}],
        # [RebalanceStrategy, {"rebalance_interval": 10}],
        # [StrategyMerger, {"strategy_classes": [[RiskMetricStrategy], [RebalanceStrategy]]}],
    ]
    simgen = StrategyGenerator(strategy_list, trading_data)
    simgen.run()
    results = simgen.get_results()

    for result in results:
        if result.name == RiskMetricStrategy.__name__:
            if optimizations.diminishing_returns:
                result.name += " + dim returns"
            if optimizations.daily_volume_correlation:
                result.name += " + 24h volume correlation"
            if not optimizations.diminishing_returns and not optimizations.daily_volume_correlation:
                result.name = "RiskMetricStrategy - no optimizations"
            result.name += " | total marketcap"

    annotation_text = (
        f"Data Range: {trading_data.dates[0].strftime(TIME_FORMAT)}--"
        f"{trading_data.dates[-1].strftime(TIME_FORMAT)} | "
        f"Data Interval: {trading_data.variables.interval_str}"
    )

    plotter = Plotter(
        trading_data,
        results,
        x_title=f"{trading_data.variables.interval_str} steps",
        y_title="Profit in $USD",
        title_text=f"Strategy Experiments ({annotation_text})",
    )

    # plotter.plot_all_symbols()
    plotter.plot_riskmetric_on_second_scale(riskmetric)
    # plotter.plot_colorcoded_riskmetric(riskmetric)

    plotter.plot_strategies()

    plotter.change_title("")
    plotter.plot_log_y_first_axis()
    plotter.show()
    # plotter.save('pdf')


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
