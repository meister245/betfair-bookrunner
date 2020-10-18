#!/usr/bin/env python3

import argparse
import json
import logging
import os
import time

from betfair_scraper import get_secrets

from bookrunner.bookrunner import BookRunner

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

logging.getLogger('urllib3').setLevel(logging.WARNING)


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('--account', action='store', type=str, default=None,
                        metavar='ACCOUNT', help='betfair account name')

    return parser.parse_args()


def get_config(name: str) -> dict:
    with open(BASE_DIR + f'/config/{name}.json', 'r') as f:
        return json.loads(f.read())


def main(account_name=None, **kwargs):
    config = get_config(name='default')
    bookrunner = BookRunner(config=config)

    if account_name:
        secrets = get_secrets(account_name)
        bookrunner.setup(secrets)

    while True:
        try:
            bookrunner.run(**kwargs)
            time.sleep(30)

        except OSError:
            time.sleep(60)
            continue


if __name__ == "__main__":
    args = parse_args()

    try:
        main(account_name=args.account)

    except KeyboardInterrupt:
        print('process aborted')
