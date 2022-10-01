from strategy.starter_strategy import StarterStrategy
from strategy.strategy import Strategy

from strategy.strategy_zero import strategy_zero
from strategy.strategy_one import strategy_one
from strategy.strategy_two import strategy_two
from strategy.strategy_three import strategy_three

"""Return the strategy that your bot should use.

:param playerIndex: A player index that can be used if necessary.

:returns: A Strategy object.
"""
def get_strategy(player_index: int) -> Strategy:  
  return strategy_one()