import os
import re


class BacktestCommon:
    data_dir = os.path.expanduser('~') + '/.bookrunner/'
    backtest_dir = data_dir + 'backtest/'

    sport = None
    market_type = None

    def __init__(self, balance=100.0):
        self.balance, self.low, self.high = balance, balance, balance
        self.total_return, self.total_stake = 0, 0
        self.count_markets, self.count_bets, self.count_bets_win, self.count_bets_lose = 0, 0, 0, 0

    @staticmethod
    def backtest_stake(name, odds_name, odds_value, stake=1.00):
        return {
            name: {
                'profit': (stake * odds_value) - stake,
                'return': stake * odds_value,
                'stake': stake,
                'type': odds_name
            }
        }

    @classmethod
    def read_history(cls, sport, market_type):
        for root, dirs, files in os.walk(cls.backtest_dir):
            for filename in files:
                if re.search(f'{sport}.+{market_type}', filename):
                    with open(root + '/' + filename, 'r') as f:
                        yield [line for line in f.read().split(
                            '\n') if len(line.strip()) > 1]

    def summary(self):
        profit = round(self.total_return - self.total_stake, 2)

        msg = [
            f'# SPORT - {self.sport} - MARKET - {self.market_type}',
            f'# BALANCE - {self.balance} - PROFIT - {profit}',
            f'# LOW - {self.low} - HIGH - {self.high}\n',

            f'# TOTAL MARKETS - {self.count_markets}',
            f'# TOTAL BETS - {self.count_bets} - BETS WON - {self.count_bets_win} - BETS LOST - {self.count_bets_lose}',
            f'# TOTAL STAKE - {self.total_stake} - TOTAL RETURN - {self.total_return}'
        ]

        for line in msg:
            print(line)

    def run(self):
        for lines in self.read_history(self.sport, self.market_type):
            self.count_markets += 1

            bets = {}

            for line in lines:
                bets = self.eval_betting_logic(bets, line)

            if len(bets) > 0:
                self.eval_bets(bets, lines[-1])

            self.update_values()

        self.summary()

    @classmethod
    def eval_betting_logic(cls, bets: dict, line: str):
        raise NotImplementedError()

    def eval_bets(self, bets: dict, last_line: dict):
        raise NotImplementedError()

    def update_values(self):
        self.balance = round(self.balance, 2)
        self.total_stake = round(self.total_stake, 2)
        self.total_return = round(self.total_return, 2)

        self.low = self.balance if self.balance < self.low else self.low
        self.high = self.balance if self.balance > self.high else self.high
