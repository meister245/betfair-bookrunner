import operator

from common import BacktestCommon


class SoccerMatchOddsHedgeBacktest(BacktestCommon):

    sport = 'soccer'
    market_type = 'match_odds'

    @staticmethod
    def unpack_line(line):
        items = line.split(',')

        odds = {
            'home': float(items[3]), 'draw': float(items[4]),
            'away': float(items[5])
        }

        scores = items[2].split('-')
        sorted_odds = sorted(odds.items(), key=operator.itemgetter(1))

        return items[0], scores, sorted_odds

    @classmethod
    def eval_betting_logic(cls, bets, line):
        game_time, scores, sorted_odds = cls.unpack_line(line)
        odds_low, odds_middle, odds_high = sorted_odds

        if game_time.isdigit() and int(game_time) >= 70:
            odds_name, odds_value = odds_low

            if 'bet_low_odds' not in bets and odds_value >= 1.44:
                stake = cls.backtest_stake(
                    'bet_low_odds', odds_name, odds_value)

                bets.update(stake)

        if game_time.isdigit() and int(game_time) >= 80:
            odds_name, odds_value = odds_low

            if 'bet_low_odds' in bets and 'bet_hedge_1' not in bets:
                if odds_name == bets['bet_low_odds']['type']:
                    stake_value = bets['bet_low_odds']['profit'] / 2
                    odds_name, odds_value = odds_middle

                    stake = cls.backtest_stake(
                        'bet_hedge_1', odds_name, odds_value, stake=stake_value)

                    bets.update(stake)

        return bets

    def eval_bets(self, bets, last_line):
        game_time, scores, sorted_odds = self.unpack_line(last_line)

        stake_sum = sum([data['stake'] for bet, data in bets.items()])

        self.balance -= stake_sum
        self.total_stake += stake_sum

        score_home, score_away = scores

        if score_home > score_away:
            for bet, data in bets.items():
                if data['type'] == 'home':
                    self.count_bets_win += 1
                    self.balance += data['return']
                    self.total_return += data['return']

                else:
                    self.count_bets_lose += 1

        elif score_home == score_away:
            for bet, data in bets.items():
                if data['type'] == 'draw':
                    self.count_bets_win += 1
                    self.balance += data['return']
                    self.total_return += data['return']

                else:
                    self.count_bets_lose += 1

        elif score_home < score_away:
            for bet, data in bets.items():
                if data['type'] == 'away':
                    self.count_bets_win += 1
                    self.balance += data['return']
                    self.total_return += data['return']

                else:
                    self.count_bets_lose += 1


if __name__ == "__main__":
    s = SoccerMatchOddsHedgeBacktest()
    s.run()
