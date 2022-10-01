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
  if (player_index == 0):
    return strategy_zero()
  elif(player_index == 1):
    return strategy_one()
  elif(player_index == 2):
    return strategy_two()
  elif(player_index == 3):
    return strategy_three()
  return Strategy()