import os

from .bookrunner import DATA_DIR, BACKTEST_DIR


if not os.path.isdir(DATA_DIR):
    os.mkdir(DATA_DIR)

if not os.path.isdir(BACKTEST_DIR):
    os.mkdir(BACKTEST_DIR)
