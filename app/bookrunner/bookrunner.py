import os
import logging
import time

from betfair_scraper.scraper import BetfairScraper
from strategy import SoccerStrategy, TennisStrategy

from .manager import BetManager

DATA_DIR = os.path.expanduser('~') + '/.bookrunner/'
BACKTEST_DIR = DATA_DIR + 'backtest/'


class BookRunner:

    def __init__(self, config: dict):
        self.logger = logging.getLogger('bookrunner')
        self.config = config

        self.bookmaker = BetfairScraper()
        self.bet_manager = BetManager(self.bookmaker)
        self.soccer = SoccerStrategy(self.bet_manager)
        self.tennis = TennisStrategy(self.bet_manager)

        self.markets = {}

    def run(self, dry_run=True):
        if not dry_run:
            self.bet_manager.sync_bets()
            self.bet_manager.update_balance()

        for market, bet, meta in self.find_bets():
            if not dry_run:
                self.process_bet(market, bet, meta)

    def setup(self, secrets: tuple):
        self.bookmaker.login(secrets)
        self.bet_manager.update_balance()

    def process_bet(self, market: dict, bet: dict, meta: dict):
        self.logger.info(
            'processing bet - %s - %s', market['sport'], market['event']
        )

        self.logger.info(
            'bet details - type: %s - odds: %s - stake: %s',
            bet['type'], bet['odds'], meta['capital-risk']
        )

        if result := self.bookmaker.submit_bet(bet, meta['capital-risk']):
            while result and \
                    market['market_id'] not in self.bet_manager.bets:
                self.bet_manager.sync_bets()

                time.sleep(3)

            self.bet_manager.sync_meta(meta)
            self.bet_manager.update_balance()

    def collect_market_history(self, sport, market_type, market):
        market_id = market['market_id']

        msg = [
            market['state']['game_time'],
            market['event']
        ]

        if sport.lower() == 'soccer':
            msg.append(
                '{}-{}'.format(
                    market['state']['scores'][0],
                    market['state']['scores'][1]
                )
            )

        msg += [x['odds'] for x in market['bets']]

        with open(BACKTEST_DIR + f'{sport}_{market_id}_{market_type}', 'a') as f:
            f.write(','.join([str(x) for x in msg]) + '\n')

    def find_bets(self):
        self.logger.debug('searching for bets')

        for sport, market_config in self.config.items():
            for market_type, market_strategies in market_config.items():
                self.logger.debug('searching bets - %s - %s',
                                  sport, market_type)

                for market in self.bookmaker.get_inplay_markets(
                        sport=sport, market_type=market_type, live_stats=True, suspended=False):

                    self.collect_market_history(sport, market_type, market)

                    for bet, meta in self.evaluate_sport_strategy(sport, market, market_strategies):
                        yield market, bet, meta

    def evaluate_sport_strategy(self, sport: str, market: dict, strategy: dict):
        if sport == 'soccer':
            for bet, meta in self.soccer.evaluate_strategy(market, strategy):
                yield bet, meta

        elif sport == 'tennis':
            for bet, meta in self.tennis.evaluate_strategy(market, strategy):
                yield bet, meta
