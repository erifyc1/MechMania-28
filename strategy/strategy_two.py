from random import Random
from game.game_state import GameState
import game.character_class

from game.item import Item
from game.player_state import PlayerState

from game.position import Position
from strategy.strategy import Strategy, can_attack, damage, generate_possible_locations, isInCenter, isOneFromCenter
from util.utility import chebyshev_distance

import logging
import numpy as np
import strategy.strategy_utils as su
import math
class strategy_two(Strategy):
    def strategy_initialize(self, my_player_index: int):
        self.has_moved = False
        return game.character_class.CharacterClass.KNIGHT

    def move_action_decision(self, game_state: GameState, my_player_index: int) -> Position:
        if not self.has_moved:
            self.home_position = game_state.player_state_list[my_player_index].position
            self.has_moved = True
        position, _ = player_two_move_strategy(game_state, my_player_index, self.home_position)
        return position

    def attack_action_decision(self, game_state: GameState, my_player_index: int) -> int:
        attack = player_two_attack_strategy_updated(game_state, my_player_index)
        logging.info("player two")
        logging.info(attack)
        return attack

    def buy_action_decision(self, game_state: GameState, my_player_index: int) -> Item:
        return Item.HUNTER_SCOPE

    def use_action_decision(self, game_state: GameState, my_player_index: int) -> bool:
        return True

def player_two_attack_strategy_updated(game_state: GameState, my_player_index: int, is_move = False):    
    our_state = game_state.player_state_list[my_player_index]
    curr_pos_attack = np.zeros(len(game_state.player_state_list))
    flags = np.zeros((len(game_state.player_state_list), 12))
    for i in range(len(game_state.player_state_list)):
        enemy_state = game_state.player_state_list[i]
        stored_enemy_position = enemy_state.position
        # make it so we don't attack ourselves
        if i == my_player_index:
            flags[i][0] = -100000 
        if su.can_attack(our_state, our_state.position, enemy_state.position):
            flags[i][0] = 1
        #if they can take center
        if can_take_center(our_state, enemy_state):
            flags[i][1] = 1
        #if we can kill them
        if su.can_kill(our_state.position, enemy_state.position, our_state, enemy_state):
            flags[i][2] = 1
        #if they can kill us attack them
        if su.can_kill(enemy_state.position, our_state.position, enemy_state, our_state):
            flags[i][3] = 1
        if su.isInCenter(enemy_state.position):
            flags[i][4] = 1
        if su.isOneFromCenter(enemy_state.position, enemy_state):
            flags[i][5] = 1
        flags[i][6] = su.hits_to_kill_enemy(our_state, enemy_state)
        flags[i][7] = su.hp(enemy_state)
        if is_move:
            enemy_moves = su.generate_possible_locations(enemy_state)
            count_of_center = 0
            count_of_one_from_center = 0
            count_of_overlap_us = 0
            count_of_overlap_them = 0
            for enemy_move in enemy_moves:
                enemy_state.position = enemy_move
                if su.isInCenter(enemy_move):
                    count_of_center += 1
                elif su.isOneFromCenter(enemy_move, enemy_state):
                    count_of_one_from_center += 1
                if can_attack(enemy_state, enemy_move, our_state.position):
                    count_of_overlap_them += 1
                if can_attack(our_state, our_state.position, enemy_move):
                    count_of_overlap_us += 1
                enemy_state.position = stored_enemy_position
            # for tomorrow: disallow attacking of unreachable players
            # if chebyshev_distance()
            flags[i][8]= count_of_overlap_them*damage(enemy_state)
            flags[i][9]= count_of_overlap_us
            flags[i][10] = count_of_center
            flags[i][11] = count_of_one_from_center * 0.2 # if enemy is one from center than add this
    curr_max = -100000000
    ignore = []
    for i in range(flags.shape[1]):
        curr_max = -100000000
        for j in range(flags.shape[0]):
            if not j == my_player_index and not j in ignore:
                curr_val = flags[j][i]
                if curr_val > curr_max:
                    curr_max = curr_val
        for j in range(flags.shape[0]):
            if flags[j][i] < curr_max:
                ignore.append(j)
    curr_pick = 0
    for i in range(flags.shape[0]):
        if i not in ignore:
            curr_pick = i
    return int(curr_pick)

def can_take_center(player_1: PlayerState, player_2: PlayerState):
    if can_attack(player_2, player_2.position, player_1.position) and (isInCenter(player_2.position) or isOneFromCenter(player_2.position, player_2)):
        htk_them = math.ceil(su.hp(player_2) / su.damage(player_1))
        htk_us = math.ceil(su.hp(player_1) / su.damage(player_2))
        return htk_them >= htk_us
    return False

def player_two_attack_strategy(game_state: GameState, my_player_index: int, is_move = False):    
    our_state = game_state.player_state_list[my_player_index]
    curr_pos_attack = np.zeros(len(game_state.player_state_list))
    flags = np.zeros((len(game_state.player_state_list), 9))
    for i in range(len(game_state.player_state_list)):
        # make it so we don't attack ourselves
        if i == my_player_index:
            curr_pos_attack[i] = -100000 
        enemy_state = game_state.player_state_list[i]
        stored_enemy_position = enemy_state.position
        # braindead ranking system
        htk = su.hits_to_kill_enemy(our_state, enemy_state)
        curr_pos_attack[i] += -htk*su.damage(our_state) + (su.hp(enemy_state) - 1) % su.damage(our_state)

        #our goal is to create a tier system, so if we can kill, then add 1000(garuntees kill)
        #if we can attack add 100 (so this creates kill, attack, neither tier)
        if su.can_attack(our_state, our_state.position, enemy_state.position):
            curr_pos_attack[i] += 100
        if su.can_kill(our_state, enemy_state):
            curr_pos_attack[i] += 1000
        if su.isInCenter(enemy_state.position):
            curr_pos_attack[i] += 5
        if su.isOneFromCenter(enemy_state.position, enemy_state):
            curr_pos_attack[i] += 1
        #if they can attack us then make it more likely that we attack them 
        if su.can_attack(enemy_state, enemy_state.position, our_state.position):
            curr_pos_attack[i] += 1*enemy_state.stat_set.damage
        #if they can kill us attack them
        if su.can_kill(enemy_state, our_state):
            curr_pos_attack[i] += 5
        if is_move:
            enemy_moves = su.generate_possible_locations(enemy_state)
            count_of_center = 0
            count_of_one_from_center = 0
            count_of_overlap_us = 0
            count_of_overlap_them = 0
            for enemy_move in enemy_moves:
                enemy_state.position = enemy_move
                if su.isInCenter(enemy_move):
                    count_of_center += 1
                elif su.isOneFromCenter(enemy_move, enemy_state):
                    count_of_one_from_center += 1
                if can_attack(enemy_state, enemy_move, our_state.position):
                    count_of_overlap_them += 1
                if can_attack(our_state, our_state.position, enemy_move):
                    count_of_overlap_us += 1
                enemy_state.position = stored_enemy_position
            # for tomorrow: disallow attacking of unreachable players
            # if chebyshev_distance()
            curr_pos_attack[i] += count_of_center
            curr_pos_attack[i] += count_of_one_from_center * 0.2 # if enemy is one from center than add this
            curr_pos_attack[i] += count_of_overlap_them*damage(enemy_state)
            curr_pos_attack[i] += count_of_overlap_us
    return int(np.argmax(curr_pos_attack))
    
def player_two_move_strategy(game_state: GameState, my_player_index: int, home_position: Position):
    our_state = game_state.player_state_list[my_player_index]
    possible_positions = su.generate_possible_locations(our_state)
    values = np.zeros(len(possible_positions))
    attacks = np.zeros(len(possible_positions))
    for idx, temp_pos in enumerate(possible_positions):
        value = -su.distance_from_center(temp_pos)
        values[idx] = value
        stored_pos = our_state.position
        our_state.position = temp_pos
        can_be_killed = False
        for i in range(len(game_state.player_state_list)):
            enemy_state = game_state.player_state_list[i]
            if not i == my_player_index:
                # if enemy can kill us decrease value 
                if su.can_kill(enemy_state.position, our_state.position, enemy_state, our_state):
                    logging.info("can be killed is checking")
                    values[idx] -= 1
            enemy_moves = su.generate_possible_locations(enemy_state)
            stored_enemy_position = enemy_state.position
            
            for enemy_move in enemy_moves:
                enemy_state.position = enemy_move
                if su.can_kill(enemy_state.position, our_state.position, enemy_state, our_state):
                    logging.info("can be killed is checking")
                    can_be_killed = True
                enemy_state.position = stored_enemy_position
        if can_be_killed:
            values[idx] -= 1
        attacks[idx] = player_two_attack_strategy_updated(game_state, my_player_index, True)
        our_state.position = stored_pos
    if our_state.item == Item.NONE and is_dominating(game_state, my_player_index) and our_state.gold >= 8:
        return (home_position, 0)
    max_index = np.argmax(values)
    best_pos = possible_positions[max_index]
    best_attack = attacks[max_index]
    return (best_pos, int(best_attack))

def is_dominating(game_state: GameState, my_player_index: int):
    our_player_score = game_state.player_state_list[my_player_index].score
    max_other_score = -1
    for i in range(len(game_state.player_state_list)):
        if not i == my_player_index:
            if game_state.player_state_list[i].score > max_other_score:
                max_other_score = game_state.player_state_list[i].score
    return our_player_score > max_other_score + 10

