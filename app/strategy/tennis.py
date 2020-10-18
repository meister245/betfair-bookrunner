from .common import StrategyCommon


class TennisStrategy(StrategyCommon):

    def __init__(self, manager):
        StrategyCommon.__init__(self, manager)

    def evaluate_strategy(self, market, strategy):
        pass
