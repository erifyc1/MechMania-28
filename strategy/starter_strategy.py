from random import Random
from game.game_state import GameState
import game.character_class

from game.item import Item

from game.position import Position
from strategy.strategy import Strategy
from util.utility import chebyshev_distance

class StarterStrategy(Strategy):
    def strategy_initialize(self, my_player_index: int):
        return game.character_class.CharacterClass.ARCHER

    def move_action_decision(self, game_state: GameState, my_player_index: int) -> Position:
        position = game_state.player_state_list[my_player_index].position
        next_pos = Position(position.x,position.y)
        if position.x == 0:
            next_pos.x = 4
        elif position.x == 9:
            next_pos.x = 5
        if position.y == 0:
            next_pos.y = 4
        elif position.y == 9:
            next_pos.y = 5



        return next_pos

    def attack_action_decision(self, game_state: GameState, my_player_index: int) -> int:
        for i in range(4):
            if i != my_player_index:
                dist = chebyshev_distance(game_state.player_state_list[my_player_index].position, game_state.player_state_list[i].position)
                if dist <= 3:
                    return i
        return my_player_index

    def buy_action_decision(self, game_state: GameState, my_player_index: int) -> Item:
        return Item.NONE

    def use_action_decision(self, game_state: GameState, my_player_index: int) -> bool:
        return False