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
        self.home_position = su.my_home_position(my_player_index)
        #self.my_index = my_player_index
        self.just_used = False
        return game.character_class.CharacterClass.ARCHER

    def move_action_decision(self, game_state: GameState, my_player_index: int) -> Position:
        logging.info(my_player_index)
        my_state = game_state.player_state_list[my_player_index]
        safe_pos = safe_positions(game_state, my_player_index)
        #and self.just_used == False
        if (my_state.gold >= 8 and my_state.item == Item.NONE ) or su.hp(my_state) == 1:
            logging.info("going back")
            return self.home_position
       #if no one is on center go
        if self.just_used == True:
            self.just_used = False
       #if health low go back
        cur_distance = su.distance_from_center(my_state.position)
        if len(safe_pos) != 0:
            # for pos in safe_pos:
            #     if su.isInCenter(pos):
            #         return pos
            for pos in safe_pos:
                if su.distance_from_center(pos) < cur_distance:
                    logging.info("moving to center")
                    return pos
            return np.random.choice(safe_pos)
        else:
            logging.info("staying")
            return my_state.position


    def attack_action_decision(self, game_state: GameState, my_player_index: int) -> int:
        _, attack = player_three_strategy(game_state, my_player_index)
        return attack

    def buy_action_decision(self, game_state: GameState, my_player_index: int) -> Item:
        my_state = game_state.player_state_list[my_player_index]
        if su.at_spawn(my_state.position, self.home_position) and my_state.gold >= 8 and my_state.item == Item.NONE:
            logging.info("bought scope")
            return Item.HUNTER_SCOPE
        return Item.NONE

    def use_action_decision(self, game_state: GameState, my_player_index: int) -> bool:
        # my_state = game_state.player_state_list[my_player_index]
        # for i in range(4):
        #     if i != my_player_index: 
        #         if my_state.item != Item.NONE and su.can_attack(my_state,my_state.position, game_state.player_state_list[i].position):
        #             self.just_used = True
        #             return True
        return False


def safe_positions(game_state: GameState, my_player_index: int):
    my_state = game_state.player_state_list[my_player_index]
    positions = su.generate_possible_locations(my_state)

    for i in range(4):
        if i != my_player_index:
            enemy_game_state = game_state.player_state_list[i]
            enemy_possible_positions = su.generate_possible_locations(enemy_game_state)

            for i in range(len(positions)-1 , -1, -1):
                for enemy_position in enemy_possible_positions:
                    if su.can_kill(positions[i], enemy_position, enemy_game_state, my_state) and not su.can_kill(enemy_position, positions[i], my_state, enemy_game_state):
                        del positions[i]
                        break
    
    return positions


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

# class strategy_three(Strategy):
#     def strategy_initialize(self, my_player_index: int):
#         self.has_moved = False
#         return game.character_class.CharacterClass.ARCHER

#     def move_action_decision(self, game_state: GameState, my_player_index: int) -> Position:
#         logging.info(my_player_index)
#         if not self.has_moved:
#             self.home_position = game_state.player_state_list[my_player_index].position
#             self.has_moved = True
#         my_state = game_state.player_state_list[my_player_index]
#         if my_state.gold >= 10 and my_state.item == Item.NONE:
#             logging.info("going to buy")
#             return self.home_position
#         positions = su.generate_possible_locations(my_state)
#         cur_distance = su.distance_from_center(my_state.position)

#         for p in positions:
#             if su.distance_from_center(p) < cur_distance:
#                 logging.info("moving to center")
#                 return p
#         logging.info("staying")
#         return my_state.position


#     def attack_action_decision(self, game_state: GameState, my_player_index: int) -> int:
#         _, attack = player_three_strategy(game_state, my_player_index)
#         return attack

#     def buy_action_decision(self, game_state: GameState, my_player_index: int) -> Item:
#         my_state = game_state.player_state_list[my_player_index]
#         #if game_state.player_state_list[my_player_index].character_class == game.character_class.CharacterClass.ARCHER:
#         if su.at_spawn(my_state.position, self.home_position) and my_state.gold >= 10 and my_state.item == Item.NONE:
#             logging.info("bought sword")
#             return Item.HEAVY_BROADSWORD
#         # elif game_state.player_state_list[my_player_index].character_class == game.character_class.CharacterClass.WIZARD:
#         #     pass
#         return Item.NONE

#     def use_action_decision(self, game_state: GameState, my_player_index: int) -> bool:
#         my_state= game_state.player_state_list[my_player_index]
#         if su.distance_from_center(my_state.position) == 0 and my_state.item != Item.NONE:
#             return True
#         return False

# def player_three_strategy(game_state: GameState, my_player_index: int):
#     our_state = game_state.player_state_list[my_player_index]
#     possible_positions = su.generate_possible_locations(our_state)
#     values = np.zeros(len(possible_positions))
#     attacks = np.zeros(len(possible_positions))
#     for idx, temp_pos in enumerate(possible_positions):
#         value = -su.distance_from_center(temp_pos)
#         values[idx] = value
#         stored_pos = our_state.position
#         curr_pos_attack = np.zeros(len(game_state.player_state_list))
#         our_state.position = temp_pos
#         for i in range(len(game_state.player_state_list)):
#             # make it so we don't attack ourselves
#             if i == my_player_index:
#                 curr_pos_attack[i] = -100000 
#                 break
#             enemy_state = game_state.player_state_list[i]
#             # braindead ranking system
#             htk = su.hits_to_kill_enemy(our_state, enemy_state)
#             curr_pos_attack[i] += -htk*su.damage(our_state) + (su.hp(enemy_state) - 1) % su.damage(our_state)
#             if su.can_attack(our_state, our_state.position, enemy_state.position):
#                 curr_pos_attack[i] += 100
#             enemy_moves = su.generate_possible_locations(enemy_state)
#             count_of_center  = 0
#             count_of_one_from_center = 0
#             count_of_overlap_us = 0
#             count_of_overlap_them = 0
#             for enemy_move in enemy_moves:
#                 if su.isInCenter(enemy_move):
#                     count_of_center += 1
#                 elif su.isOneFromCenter(enemy_move, enemy_state):
#                     count_of_one_from_center += 1
#             # for tomorrow: disallow attacking of unreachable players
#             # if chebyshev_distance()
#             curr_pos_attack[i] += count_of_center
#             curr_pos_attack[i] += count_of_one_from_center * 0.2 # if enemy is one from center than add this 

#         attacks[idx] = np.argmax(curr_pos_attack)
#         our_state.position = stored_pos
#     max_index = np.argmax(values)
#     best_pos = possible_positions[max_index]
#     best_attack = attacks[max_index]
#     if my_player_index == 1: 
#         logging.info(best_attack)
#     return (best_pos, int(best_attack))


