"""
File for testing functionality of the DCA strategy class.
"""

import pytest
from utils import get_data_from_dict, update_close_values

from backtester.dca_strategy import DCAStrategy
from backtester.utils import BTC_SYMBOL, create_portfolio_from_data


@pytest.fixture
def data():
    return get_data_from_dict("2022-01-01", "2022-01-05", "1d", {"BTCUSDT"})


@pytest.fixture
def usd():
    return 0


@pytest.fixture
def portfolio(data, usd):
    return create_portfolio_from_data(data, usd)


@pytest.fixture
def strategy(data, portfolio):
    new_close_values = {"BTCUSDT": [10, 20, 30, 20, 10]}
    data.data = update_close_values(data, new_close_values)
    strategy = DCAStrategy(data, portfolio=portfolio)
    return strategy


def test_dca(strategy):
    assert strategy.portfolio.usd == 0
    assert strategy.portfolio.coins[BTC_SYMBOL] == 0

    execute_step_and_assert_portfolio(strategy, 0, 0.5)
    execute_step_and_assert_portfolio(strategy, 0, 0.5 + 5 / 20)
    execute_step_and_assert_portfolio(strategy, 0, 0.5 + 5 / 20 + 5 / 30)
    execute_step_and_assert_portfolio(strategy, 0, 0.5 + 5 / 20 + 5 / 30 + 5 / 20)
    execute_step_and_assert_portfolio(strategy, 0, 0.5 + 5 / 20 + 5 / 30 + 5 / 20 + 0.5)


def execute_step_and_assert_portfolio(strategy, usdvalue, btcvalue):
    strategy.current_step = strategy.steps[strategy.i]
    strategy.execute_step()
    strategy.i += 1
    assert strategy.portfolio.usd == usdvalue
    assert strategy.portfolio.coins[BTC_SYMBOL] == btcvalue
