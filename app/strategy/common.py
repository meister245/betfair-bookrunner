import logging

class MarketConditionException(Exception):
    pass


class StrategyCommon:

    def __init__(self, manager):
        self.logger = logging.getLogger(__name__)
        self.bet_manager = manager

    def validate_betting_constraints(self, market, strategy):
        self.validate_is_strategy_max_active(strategy)
        self.validate_is_strategy_active(market, strategy)
        self.validate_game_time(market, strategy)
        self.validate_odds(market, strategy)
        self.validate_stake(strategy)

    def validate_is_strategy_active(self, market, strategy):
        market_id, strategy_name = market['market_id'], strategy['name']

        if market['market_id'] in self.bet_manager.meta:
            for bet_id, data in self.bet_manager.meta[market_id]:
                if data['strategy'] == strategy_name:
                    raise MarketConditionException(
                        f'strategy {strategy_name} already exists on market {market_id}')

    def validate_is_strategy_max_active(self, strategy):
        active_bets, max_active = 0, strategy.get('max_active', 0)

        for market_id, meta_data in self.bet_manager.meta.items():
            for bet_id, data in meta_data.items():
                if data['strategy'] == strategy['mapping']:
                    active_bets += 1

        if max_active != 0 and active_bets >= max_active:
            raise MarketConditionException(
                f'maximum number of bets reached for strategy {strategy["mapping"]}')

    def validate_stake(self, strategy):
        if strategy.get('stake', 0.11) > self.bet_manager.balance:
            raise MarketConditionException('insufficient balance for betting')

    @classmethod
    def validate_odds(cls, market, strategy):
        sorted_odds = cls.get_sorted_odds(market)
        bet_odds_low = sorted_odds[0]['odds']

        if min_odds := strategy.get('min_odds', False):
            if bet_odds_low < min_odds:
                raise MarketConditionException(
                    'market odds not compatible')

        if max_odds := strategy.get('max_odds', False):
            if bet_odds_low > max_odds:
                raise MarketConditionException(
                    'market odds not compatible')

    @classmethod
    def validate_game_time(cls, market, strategy):
        game_time = market['state']['game_time']

        if min_game_time := strategy.get('min_game_time', False):
            if isinstance(game_time, int) and game_time < min_game_time:
                raise MarketConditionException(
                    'market game time not compatible')

        if max_game_time := strategy.get('max_game_time', False):
            if isinstance(game_time, int) and game_time > max_game_time:
                raise MarketConditionException(
                    'market game time not compatible')

        if min_game_time or max_game_time:
            if not isinstance(game_time, int):
                raise MarketConditionException(
                    'market game time not available')

    @staticmethod
    def get_sorted_odds(market):
        return sorted(market['bets'], key=lambda x: x['odds'])

    def generate_bet_meta(self, bet, config, market):
        self.logger.debug(
            'generating bet meta - %s - %s - %s',
            market['market_id'], market['event'], config['name']
        )

        capital_risk = config['stake']
        capital_return = capital_risk * bet['odds']
        capital_profit = capital_return - capital_risk

        meta = {
            'name': config['name'],
            'sport': market['sport'],
            'strategy': config['mapping'],
            'event': market['event'],
            'type': bet['type'].upper(),
            'capital-risk': float('{:.2f}'.format(capital_risk)),
            'capital-return': float('{:.2f}'.format(capital_return)),
            'capital-profit': float('{:.2f}'.format(capital_profit))
        }

        if hedge_ratio := config.get('hedge_ratio', False):
            capital_hedge = capital_profit * hedge_ratio / 100
            meta.update(
                {'capital-hedge': float('{:.2f}'.format(capital_hedge))})

        return meta
