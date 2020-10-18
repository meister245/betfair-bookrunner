import json
import logging
import os

DATA_DIR = os.path.expanduser('~') + '/.bookrunner'
RESULTS_FILE = DATA_DIR + 'results'


class BetManager:

    def __init__(self, bookmaker):
        self.logger = logging.getLogger('bet-manager')
        self.bookmaker = bookmaker

        self.balance = 0
        self.bets = {}
        self.meta = {}

    def update_balance(self):
        self.logger.debug('updating wallet balance')
        self.balance = self.bookmaker.get_balance()

    def sync_bets(self):
        self.logger.debug('syncing bets')

        for item in self.bookmaker.get_bet_activity(status='open'):
            if item['market_id'] not in self.bets:
                self.bets['market_id'] = {}
                self.logger.debug(
                    'registering market ID - %s', item['market_id'])

            if item['bet_id'] not in self.bets['market_id']:
                self.bets['market_id']['bet_id'] = item
                self.logger.debug(
                    'registering bet ID - %s', item['bet_id'])

        for item in self.bookmaker.get_bet_activity(status='settled'):
            if item['market_id'] not in self.bets:
                continue

            if item['bet_id'] in self.bets[item['market_id']]:
                result = self.bets['market_id'].pop(item['bet_id'], None)

                with open(RESULTS_FILE, 'a') as f:
                    f.write(json.dumps(result) + '\n')

                self.logger.debug(
                    'writing bet ID result to file - %s', item['bet_id'])

            if len(self.bets['market_id']) == 0:
                self.bets.pop(item['market_id'], None)
                self.logger.debug(
                    'removing market ID - %s', item['market_id'])

    def sync_meta(self, meta):
        self.logger.debug('syncing meta')

        if meta['market_id'] in self.bets and \
                meta['market_id'] not in self.meta:
            self.meta[meta['market_id']] = {}

        for market_id, bet_data in self.bets.items():
            if not market_id == meta['market_id']:
                continue

            for bet_id, data in bet_data.items():
                if not data['stake'] == meta['capital-risk']:
                    continue

                if not data['type'] == meta['type']:
                    continue

                if not data['event'] == meta['event']:
                    continue

                self.meta[market_id] = self.meta.pop(market_id, {})
                self.meta[market_id][bet_id] = meta

                self.logger.debug(
                    'registering bet ID meta - %s', bet_id)

        for market_id in tuple(self.meta):
            if market_id not in self.bets:
                self.meta.pop(market_id, None)

                self.logger.debug(
                    'removing market ID meta - %s', market_id)
