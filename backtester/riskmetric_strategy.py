"""
File defining the risk metric strategy.
"""


from .strategy import Strategy
from .utils import Portfolio, TradingData, get_risk_metric


class RiskMetricStrategy(Strategy):
    def __init__(self, data: TradingData, portfolio: Portfolio = None):
        super().__init__(data, portfolio)
        self.riskmetric = get_risk_metric(data.btc_historical, self.steps[0], self.steps[-1])
        self.threshold = 0.7
        self.states = {
            "sell": False,
            0.7: False,
            0.6: False,
            0.5: False,
            0.4: False,
            0.3: False,
            0.2: False,
            0.1: False,
        }

    def execute_step(self):
        super().execute_step()
        risk = self.riskmetric.loc[self.current_step]["riskmetric"]

        if risk < 0.1:
            if not self.states[0.1]:
                self.states = self.set_states(0.1)
                self.sell()
                self.buy()
        elif risk < 0.2:
            if not self.states[0.2]:
                self.states = self.set_states(0.2)
                self.sell()
                self.buy()
        elif risk < 0.3:
            if not self.states[0.3]:
                self.states = self.set_states(0.3)
                self.sell()
                self.buy()
        elif risk < 0.4:
            if not self.states[0.4]:
                self.states = self.set_states(0.4)
                self.buy_percentage(0.8)
        elif risk < 0.5:
            if not self.states[0.5]:
                self.states = self.set_states(0.5)
                self.buy_percentage(0.6)
        elif risk < 0.6:
            if not self.states[0.6]:
                self.states = self.set_states(0.6)
                self.buy_percentage(0.4)
        elif risk < 0.7:
            if not self.states[0.7]:
                self.states = self.set_states(0.7)
                self.buy_percentage(0.2)
        else:
            if not self.sold_state:
                self.sell()
                self.sold_state = True
                self.bought_state = True

    def set_states(self, state_to_set):
        self.states = {k: False for k in self.states}
        self.states[state_to_set] = True
        self.sold_state = False
        return self.states

    def buy_percentage(self, percent):
        self.bought_dates.append(self.current_step)
        coins = self.portfolio.coins

        # print(self.riskmetric.loc[self.current_step]['riskmetric'])
        # print(self.current_step)
        # print(self.portfolio.usd)
        # print(coins)

        self.sell()

        # print(self.portfolio.usd)
        # print(coins)

        usd_to_buy_coins_with = self.portfolio.usd * percent
        usd_to_buy_one_coin_with = usd_to_buy_coins_with / len(coins)
        for coin in coins:
            close = self.get_close_value(coin)
            self.portfolio.coins[coin] += usd_to_buy_one_coin_with / close

        self.portfolio.usd = self.portfolio.usd - usd_to_buy_coins_with

        # print(usd_to_buy_coins_with, usd_to_buy_one_coin_with)
        # print(coins)
        # print(self.portfolio.usd)
        # print()
