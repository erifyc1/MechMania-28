from random import Random
from turtle import pos
from game.game_state import GameState
import game.character_class

from game.item import Item

from game.position import Position
from strategy.strategy import Strategy
from strategy.strategy_utils import choosePositionAndAttack
from util.utility import chebyshev_distance
import logging
import numpy as np
import strategy.strategy_utils as su

class strategy_zero(Strategy):
    def strategy_initialize(self, my_player_index: int):
        self.home = Position(9 * (my_player_index % 2), 9 * (my_player_index // 2))
        self.waypoints = [Position(1, 1), Position(2, 2), Position(3, 3), Position(4, 4)]
        self.followed_waypoints = False
        if self.home.x == 9:
            self.waypoints[0].x = 8
            self.waypoints[1].x = 7
            self.waypoints[2].x = 6
            self.waypoints[3].x = 5

        if self.home.y == 9:
            self.waypoints[0].y = 8
            self.waypoints[1].y = 7
            self.waypoints[2].y = 6
            self.waypoints[3].y = 5
        

        return game.character_class.CharacterClass.KNIGHT

    def move_action_decision(self, game_state: GameState, my_player_index: int) -> Position:
        state = game_state.player_state_list[my_player_index]
        if state.position.x == self.home.x and state.position.y == self.home.y:
            self.followed_waypoints = False
            return self.waypoints[0]
        if not self.followed_waypoints and state.position.x == self.waypoints[0].x and state.position.y == self.waypoints[0].y:
            return self.waypoints[1]
        if not self.followed_waypoints and state.position.x == self.waypoints[1].x and state.position.y == self.waypoints[1].y:
            if su.speed(state) == 4:
                return self.waypoints[3]
            else:
                return self.waypoints[2]
        if not self.followed_waypoints and state.position.x == self.waypoints[2].x and state.position.y == self.waypoints[2].y:
            return self.waypoints[3]
        if not self.followed_waypoints and state.position.x == self.waypoints[3].x and state.position.y == self.waypoints[3].y:
            self.followed_waypoints = True
        position = player_zero_strategy(game_state, my_player_index)
        if state.health < 3:
            return self.home
        return position

    def attack_action_decision(self, game_state: GameState, my_player_index: int) -> int:
        state = game_state.player_state_list[my_player_index]
        best_attack = determine_best_attack(state.position, game_state, my_player_index)[0]
        return best_attack

    def buy_action_decision(self, game_state: GameState, my_player_index: int) -> Item:
        state = game_state.player_state_list[my_player_index]
        item = state.item
        if item == Item.NONE and state.gold >= 8 and state.position.x == self.home.x and state.position.y == self.home.y:
            return Item.HUNTER_SCOPE
        else:
            return Item.NONE

    def use_action_decision(self, game_state: GameState, my_player_index: int) -> bool:
        state = game_state.player_state_list[my_player_index]
        item = state.item
        return False
        return item == Item.SPEED_POTION and state.position.x == self.waypoints[1].x and state.position.y == self.waypoints[1].y

def player_zero_strategy(game_state: GameState, my_player_index: int):
    player_state = game_state.player_state_list[my_player_index]
    
    possible_positions = su.generate_possible_locations(player_state)
    tile_values = np.zeros(len(possible_positions))
    for idx, possible_pos in enumerate(possible_positions):
        tile_values[idx] = 0
        # worse distance squared from center
        tile_values[idx] -= su.distance_from_center(possible_pos)**2

        # better based on attack possibility
        best_attack_from_position = determine_best_attack(possible_pos, game_state, my_player_index)
        tile_values[idx] += best_attack_from_position[1]

        # better when not next to multiple enemies
        in_range = enemies_in_range(possible_pos, game_state, my_player_index)
        tile_values[idx] += -(in_range**3) + 2


    best_idx = np.argmax(tile_values)
    best_pos = possible_positions[best_idx]
    return best_pos

def determine_best_attack(tile: Position, game_state: GameState, my_player_index: int): # tuple(player_num, value)
    player_state = game_state.player_state_list[my_player_index]
    original_position = player_state.position
    player_state.position = tile

    best_attack = (my_player_index, -1000)
    for enemy_id, enemy_state in enumerate(game_state.player_state_list):
        if enemy_id == my_player_index or chebyshev_distance(player_state.position, enemy_state.position) > su.attack_range(player_state):
            pass # logging.info("failed: " + str(enemy_id) + " because " + str(my_player_index) + ", " + str(chebyshev_distance(player_state.position, enemy_state.position)))
        # htk value
        htk = su.hits_to_kill_enemy(player_state, enemy_state)
        htk_value = -htk * su.damage(player_state) + (su.hp(enemy_state) - 1) % su.damage(player_state)

        # class value
        cv = su.class_value(enemy_state) + su.damage(enemy_state)

        attack_value = htk_value + 0.3 * cv
        if attack_value > best_attack[1]:
            best_attack = (enemy_id, attack_value)

    player_state.position = original_position
    return best_attack

def enemies_in_range(tile: Position, game_state: GameState, my_player_index: int) -> int:
    player_state = game_state.player_state_list[my_player_index]
    in_range = 0
    for enemy_id, enemy_state in enumerate(game_state.player_state_list):
        if enemy_id == my_player_index:
            break
        if chebyshev_distance(enemy_state.position, player_state.position) <= su.attack_range(enemy_state):
            in_range += 1
    return in_range



# if su.can_attack(our_state, our_state.position, enemy_state.position):
#     curr_pos_attack[i] += 100
# enemy_moves = su.generate_possible_locations(enemy_state)
# count_of_center  = 0
# count_of_one_from_center = 0
# count_of_overlap_us = 0
# count_of_overlap_them = 0
# for enemy_move in enemy_moves:
#     if su.isInCenter(enemy_move):
#         count_of_center += 1
#     elif su.isOneFromCenter(enemy_move, enemy_state):
#         count_of_one_from_center += 1
# # for tomorrow: disallow attacking of unreachable players
# # if chebyshev_distance()
# curr_pos_attack[i] += count_of_center
# curr_pos_attack[i] += count_of_one_from_center * 0.2 # if enemy is one from center than add this 