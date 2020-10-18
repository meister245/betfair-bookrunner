import logging

from .common import MarketConditionException, StrategyCommon


class SoccerStrategy(StrategyCommon):

    def __init__(self, manager):
        StrategyCommon.__init__(self, manager)
        self.logger = logging.getLogger('soccer')

    def evaluate_strategy(self, market, strategy):
        for item in strategy:

            try:
                if item['mapping'] == 'home-away':
                    if bet_config := self.home_away(market, item):
                        yield bet_config

                elif item['mapping'] == 'hedge-home-away':
                    if bet_config := self.hedge_home_away(market, item):
                        yield bet_config

            except MarketConditionException:
                continue

    def home_away(self, market, config):
        self.validate_betting_constraints(market, config)

        if scores := market['state']['scores']:
            if abs(scores[0] - scores[1]) != 1:
                raise MarketConditionException(
                    'score difference not equal to 1')

        sorted_odds = self.get_sorted_odds(market)
        bet_odds = sorted_odds[0]

        if bet_odds['type'] not in ['HOME', 'AWAY']:
            raise MarketConditionException('lowest odds bet is DRAW type')

        return bet_odds, self.generate_bet_meta(bet_odds, config, market)

    def hedge_home_away(self, market, config):
        self.validate_betting_constraints(market, config)

        parent_bet_meta = None
        market_id = market['market_id']

        if market_id not in self.bet_manager.meta:
            raise MarketConditionException('no existing bet for market')

        for bet_id, bet_data in self.bet_manager.meta[market_id].items():
            if config['parent_bet'] == bet_data['name']:
                parent_bet_meta = bet_data
                break

        if parent_bet_meta is None:
            raise MarketConditionException('parent bet does not exist')

        if scores := market['state']['scores']:
            if abs(scores[0] - scores[1]) != 1:
                raise MarketConditionException(
                    'score difference not equal to 1')

        sorted_odds = self.get_sorted_odds(market)
        bet_odds = sorted_odds[1]

        if bet_odds['type'] != 'DRAW':
            raise MarketConditionException('lowest odds bet is not DRAW type')

        if capital_hedge := parent_bet_meta.get('capital-hedge', False):
            hedge_stake = capital_hedge * config['hedge_stake_percent'] / 100

            if hedge_stake < 0.11:
                raise MarketConditionException('hedge capital too low')

            config.update({
                'stake': float('{:.2f}'.format(hedge_stake))
            })

        if 'stake' not in config:
            raise MarketConditionException('missing capital hedge information')

        return bet_odds, self.generate_bet_meta(bet_odds, config, market)
