"""
File for testing basic buy and sell functionality of the strategy class.
"""

import pytest
from utils import get_data_from_dict, update_close_values

from backtester.strategy import Strategy
from backtester.utils import (
    BTC_SYMBOL,
    Portfolio,
    TradingData,
    create_portfolio_from_data,
    set_index_for_data,
)


class GeneralStrategy(Strategy):
    def __init__(self, data: TradingData, portfolio: Portfolio = None):
        super().__init__(data, portfolio)
        self.buy()

    def execute_step(self):
        super().execute_step()


@pytest.fixture
def data():
    return get_data_from_dict("2022-01-01", "2022-01-01", "1d", {"BTCUSDT"})


@pytest.fixture
def usd():
    return 10


@pytest.fixture
def portfolio(data, usd):
    return create_portfolio_from_data(data, usd)


@pytest.fixture
def strategy(data, portfolio):
    new_close_values = {"BTCUSDT": [10]}
    data.data = update_close_values(data, new_close_values)
    strategy = GeneralStrategy(data, portfolio=portfolio)
    return strategy


def test_regular_buy(strategy):
    assert strategy.portfolio.usd == 0
    assert strategy.portfolio.coins[BTC_SYMBOL] == 1

    assert strategy.buy() == -1

    strategy.execute_buy_logic()
    assert strategy.portfolio.usd == 0
    assert strategy.portfolio.coins[BTC_SYMBOL] == 1

    strategy.portfolio.usd = 0
    strategy.portfolio.coins[BTC_SYMBOL] = 0
    strategy.buy()
    assert strategy.portfolio.usd == 0
    assert strategy.portfolio.coins[BTC_SYMBOL] == 0


def test_regular_sell(strategy):
    assert strategy.sell() == 0
    assert strategy.portfolio.usd == 10
    assert strategy.portfolio.coins[BTC_SYMBOL] == 0

    assert strategy.sell() == -1

    strategy.execute_sell_logic()
    assert strategy.portfolio.usd == 10
    assert strategy.portfolio.coins[BTC_SYMBOL] == 0


def test_buy_partial(strategy):
    assert strategy.portfolio.usd == 0
    assert strategy.portfolio.coins[BTC_SYMBOL] == 1

    strategy.buy_partial(10)
    assert strategy.portfolio.usd == 9
    assert strategy.portfolio.coins[BTC_SYMBOL] == 1 / 10

    strategy.buy_partial(50)
    assert strategy.portfolio.usd == 5
    assert strategy.portfolio.coins[BTC_SYMBOL] == 5 / 10

    strategy.buy_partial(10)
    assert strategy.portfolio.usd == 9
    assert strategy.portfolio.coins[BTC_SYMBOL] == 1 / 10

    strategy.buy_partial(90)
    assert strategy.portfolio.usd == 1
    assert strategy.portfolio.coins[BTC_SYMBOL] == 9 / 10

    strategy.buy_partial(100)
    assert strategy.portfolio.usd == 0
    assert strategy.portfolio.coins[BTC_SYMBOL] == 10 / 10

    strategy.buy_partial(0)
    assert strategy.portfolio.usd == 10
    assert strategy.portfolio.coins[BTC_SYMBOL] == 0 / 10

    strategy.buy_partial(10)
    assert strategy.portfolio.usd == 9
    assert strategy.portfolio.coins[BTC_SYMBOL] == 1 / 10

    strategy.buy()
    assert strategy.portfolio.usd == 0
    assert strategy.portfolio.coins[BTC_SYMBOL] == 1

    strategy.buy_partial(10)
    assert strategy.portfolio.usd == 9
    assert strategy.portfolio.coins[BTC_SYMBOL] == 1 / 10

    strategy.sell()
    assert strategy.portfolio.usd == 10
    assert strategy.portfolio.coins[BTC_SYMBOL] == 0


def test_sell_partial(strategy):
    assert strategy.portfolio.usd == 0
    assert strategy.portfolio.coins[BTC_SYMBOL] == 1

    strategy.sell_partial(90)
    assert strategy.portfolio.usd == 9
    assert strategy.portfolio.coins[BTC_SYMBOL] == 1 / 10

    strategy.sell_partial(50)
    assert strategy.portfolio.usd == 5
    assert strategy.portfolio.coins[BTC_SYMBOL] == 5 / 10

    strategy.sell_partial(90)
    assert strategy.portfolio.usd == 9
    assert strategy.portfolio.coins[BTC_SYMBOL] == 1 / 10

    strategy.sell_partial(10)
    assert strategy.portfolio.usd == 1
    assert strategy.portfolio.coins[BTC_SYMBOL] == 9 / 10

    strategy.sell_partial(0)
    assert strategy.portfolio.usd == 0
    assert strategy.portfolio.coins[BTC_SYMBOL] == 10 / 10

    strategy.sell_partial(100)
    assert strategy.portfolio.usd == 10
    assert strategy.portfolio.coins[BTC_SYMBOL] == 0 / 10

    strategy.sell_partial(90)
    assert strategy.portfolio.usd == 9
    assert strategy.portfolio.coins[BTC_SYMBOL] == 1 / 10

    strategy.buy()
    assert strategy.portfolio.usd == 0
    assert strategy.portfolio.coins[BTC_SYMBOL] == 1

    strategy.sell_partial(90)
    assert strategy.portfolio.usd == 9
    assert strategy.portfolio.coins[BTC_SYMBOL] == 1 / 10

    strategy.sell()
    assert strategy.portfolio.usd == 10
    assert strategy.portfolio.coins[BTC_SYMBOL] == 0


def test_buy_additional(strategy):
    assert strategy.portfolio.usd == 0
    assert strategy.portfolio.coins[BTC_SYMBOL] == 1

    strategy.buy_additional(10)
    assert strategy.portfolio.usd == 0
    assert strategy.portfolio.coins[BTC_SYMBOL] == 2

    strategy.buy_additional(10)
    assert strategy.portfolio.usd == 0
    assert strategy.portfolio.coins[BTC_SYMBOL] == 3

    strategy.buy_additional(5)
    assert strategy.portfolio.usd == 0
    assert strategy.portfolio.coins[BTC_SYMBOL] == 3.5

    strategy.buy()
    assert strategy.portfolio.usd == 0
    assert strategy.portfolio.coins[BTC_SYMBOL] == 3.5

    strategy.sell()
    assert strategy.portfolio.usd == 35
    assert strategy.portfolio.coins[BTC_SYMBOL] == 0

    strategy.buy_additional(10)
    assert strategy.portfolio.usd == 35
    assert strategy.portfolio.coins[BTC_SYMBOL] == 1
