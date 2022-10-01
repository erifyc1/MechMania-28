from random import Random
from game.game_state import GameState
import game.character_class

from game.item import Item

from game.position import Position
from strategy.strategy import Strategy
from util.utility import chebyshev_distance

import logging
import numpy as np
import strategy.strategy_utils as su

class strategy_three(Strategy):
    def strategy_initialize(self, my_player_index: int):
        choice = np.random.randint(0,3)
        if choice == 0:
            return game.character_class.CharacterClass.ARCHER
        if choice == 1:
            return game.character_class.CharacterClass.WIZARD
        return game.character_class.CharacterClass.KNIGHT

    def move_action_decision(self, game_state: GameState, my_player_index: int) -> Position:
        position, _ = player_three_strategy(game_state, my_player_index)
        return position

    def attack_action_decision(self, game_state: GameState, my_player_index: int) -> int:
        _, attack = player_three_strategy(game_state, my_player_index)
        return attack

    def buy_action_decision(self, game_state: GameState, my_player_index: int) -> Item:
        return Item.NONE

    def use_action_decision(self, game_state: GameState, my_player_index: int) -> bool:
        return False

def player_three_strategy(game_state: GameState, my_player_index: int):
    our_state = game_state.player_state_list[my_player_index]
    possible_positions = su.generate_possible_locations(our_state)
    values = np.zeros(len(possible_positions))
    attacks = np.zeros(len(possible_positions))
    for idx, temp_pos in enumerate(possible_positions):
        value = -su.distance_from_center(temp_pos)
        values[idx] = value
        stored_pos = our_state.position
        curr_pos_attack = np.zeros(len(game_state.player_state_list))
        our_state.position = temp_pos
        for i in range(len(game_state.player_state_list)):
            # make it so we don't attack ourselves
            if i == my_player_index:
                curr_pos_attack[i] = -100000 
                break
            enemy_state = game_state.player_state_list[i]
            # braindead ranking system
            htk = su.hits_to_kill_enemy(our_state, enemy_state)
            curr_pos_attack[i] += -htk*su.damage(our_state) + (su.hp(enemy_state) - 1) % su.damage(our_state)
            if su.can_attack(our_state, our_state.position, enemy_state.position):
                curr_pos_attack[i] += 100
            enemy_moves = su.generate_possible_locations(enemy_state)
            count_of_center  = 0
            count_of_one_from_center = 0
            count_of_overlap_us = 0
            count_of_overlap_them = 0
            for enemy_move in enemy_moves:
                if su.isInCenter(enemy_move):
                    count_of_center += 1
                elif su.isOneFromCenter(enemy_move, enemy_state):
                    count_of_one_from_center += 1
            # for tomorrow: disallow attacking of unreachable players
            # if chebyshev_distance()
            curr_pos_attack[i] += count_of_center
            curr_pos_attack[i] += count_of_one_from_center * 0.2 # if enemy is one from center than add this 

        attacks[idx] = np.argmax(curr_pos_attack)
        our_state.position = stored_pos
    max_index = np.argmax(values)
    best_pos = possible_positions[max_index]
    best_attack = attacks[max_index]
    if my_player_index == 1: 
        logging.info(best_attack)
    return (best_pos, int(best_attack))