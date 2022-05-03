"""
File for orchestrating the various strategies in play.
"""

import logging
from copy import deepcopy

from .dca_strategy import DCAStrategy
from .hodl_strategy import HodlStrategy
from .plotter import Plotter
from .rebalance_strategy import RebalanceStrategy
from .riskmetric_strategy import RiskMetricStrategy
from .strategy import Strategy
from .utils import (
    BTC_SYMBOL,
    TIME_FORMAT,
    Portfolio,
    StrategyResult,
    TradingData,
    create_portfolio_from_data,
    get_dates_from_index,
    noop,
    transform_historical_btc_to_trading_data,
)

# HACK: Imports will not be removed automatically by formatter.
HodlStrategy
RebalanceStrategy
RiskMetricStrategy
DCAStrategy


def simulate(trading_data: TradingData):
    logging.info("Running simulation")

    # get historic BTC data if BTC is the only coin considered
    if trading_data.symbols == {BTC_SYMBOL} and trading_data.variables.interval_str == "1d":
        start_date = "2014-02-01"
        trading_data.data = transform_historical_btc_to_trading_data(
            trading_data.btc_historical, start_date
        )
        trading_data.dates = get_dates_from_index(trading_data.data)
    # print(trading_data.data)

    strategy_list = [
        [HodlStrategy],
        [RebalanceStrategy],
        # [RiskMetricStrategy],
        # [RiskMetricStrategy, {"metric": "total_marketcap"}],
        [RebalanceStrategy, {"rebalance_interval": 5}],
        [RebalanceStrategy, {"rebalance_interval": 10}],
        # [RiskMetricStrategy],
        # [RiskMetricStrategy, {"metric": "total_marketcap"}],
        # [StrategyMerger, {"strategy_classes": [[RiskMetricStrategy], [RebalanceStrategy]]}],
        # [
        # StrategyMerger,
        # {
        # "strategy_classes": [
        # [RiskMetricStrategy],
        # [RebalanceStrategy, {"rebalance_interval": 5}],
        # ]
        # },
        # ],
    ]
    simgen = StrategyGenerator(strategy_list, trading_data)

    simgen.run()
    results = simgen.get_results()

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

    # plotter.change_title("")
    # plotter.plot_historical_btc()
    # plotter.plot_historical_btc_riskmetric_on_second_scale()

    # plotter.plot_strategies()
    # plotter.plot_all_symbols()

    plotter.plot_strategies_as_percentages()
    plotter.plot_all_symbols_as_percentages()
    plotter.show()
    plotter.reset_traces()

    plotter.plot_unlog_y_first_axis()
    plotter.plot_strategies_as_percentages()
    plotter.show()
    plotter.reset_traces()

    plotter.plot_strategies()
    plotter.plot_all_symbols()
    plotter.show_both_log_and_linear()
    plotter.reset_traces()

    # plotter.change_title("Colorcoded Risk Metric")
    # plotter.plot_historical_btc_colorcoded_riskmetric()
    # plotter.show_both_log_and_linear()


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

    def get_results(self):
        results = []
        for strategy in self.strategies:
            result = StrategyResult(
                strategy.name, strategy.profits_in_time, strategy.bought_dates, strategy.sold_dates
            )
            results.append(result)
            logging.info(f"{result.name}: {result.profits[-1]}")
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
