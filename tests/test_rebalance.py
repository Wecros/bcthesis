"""
File for testing basic functionality of the implemented rebalance strategy.
"""

import pytest
from utils import get_data_from_dict, update_close_values

from backtester.rebalance_strategy import RebalanceStrategy
from backtester.utils import create_portfolio_from_data


@pytest.fixture
def data():
    return get_data_from_dict("2022-01-01", "2022-01-02", "1d", {"BTCUSDT", "ETHUSDT"})


@pytest.fixture
def usd():
    return 20


@pytest.fixture
def portfolio(data, usd):
    return create_portfolio_from_data(data, usd)


def test_rebalance_strategy(data, portfolio):
    new_close_values = {"BTCUSDT": [10, 20], "ETHUSDT": [10, 10]}
    data.data = update_close_values(data, new_close_values)

    strategy = RebalanceStrategy(data, portfolio)

    execute_step_and_assert_portfolio(strategy, 1, 1)
    execute_step_and_assert_portfolio(strategy, 1.5, 0.75)


def execute_step_and_assert_portfolio(strategy, ethvalue, btcvalue):
    strategy.current_step = strategy.steps[strategy.i]
    strategy.execute_step()
    strategy.i += 1
    assert strategy.portfolio.coins["ETHUSDT"] == ethvalue
    assert strategy.portfolio.coins["BTCUSDT"] == btcvalue
