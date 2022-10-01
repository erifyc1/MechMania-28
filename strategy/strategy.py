from abc import abstractmethod
from game.game_state import GameState
from game.item import Item
from game.player_state import PlayerState
from game.position import Position
import game.character_class
from util.utility import manhattan_distance, chebyshev_distance
import math
import numpy as np
import logging

class Strategy(object):
    """Before the game starts, pick a class for your bot to start with.

    :returns: A game.CharacterClass Enum.
    """
    @abstractmethod
    def strategy_initialize(self, my_player_index: int) -> None:
        self.index = my_player_index
        self.curr_action = Position(0,0)
        self.curr_pos_attack = 0
        if my_player_index == 0:
            return game.character_class.CharacterClass.KNIGHT
        if my_player_index == 1:
            return game.character_class.CharacterClass.WIZARD
        if my_player_index == 2:
            return game.character_class.CharacterClass.WIZARD
        else:
            return game.character_class.CharacterClass.KNIGHT

    """Each turn, decide if you should use the item you're holding. Do not try to use the
    legendary Item.None!

    :param gameState:     A provided GameState object, contains every piece of info on the game board.
    :param myPlayerIndex: You may find out which player on the board you are.

    :returns: If you want to use your item
    """
    @abstractmethod
    def use_action_decision(self, game_state: GameState, my_player_index: int) -> bool:
        return True

    """Each turn, pick a position on the board that you want to move towards. Be careful not to
    fall out of the board!

    :param gameState:     A provided GameState object, contains every piece of info on the game board.
    :param myPlayerIndex: You may find out which player on the board you are.

    :returns: A game.Position object.
    """
    @abstractmethod
    def move_action_decision(self, game_state: GameState, my_player_index: int) -> Position:
        # our_player = game_state.player_state_list[my_player_index]
        # our_player.position = self.curr_action
        if (my_player_index == 1 or my_player_index == 2 or my_player_index == 3 or my_player_index == 0):
            pos, _  = choosePositionAndAttack(game_state, my_player_index)
            return pos
        return Position(0,0)

    """Each turn, pick a player you would like to attack. Feel free to be a pacifist and attack no
    one but yourself.

    :param gameState:     A provided GameState object, contains every piece of info on the game board.
    :param myPlayerIndex: You may find out which player on the board you are.

    :returns: Your target's player index.
    """
    @abstractmethod
    def attack_action_decision(self, game_state: GameState, my_player_index: int) -> int:
        _, attack = choosePositionAndAttack(game_state, my_player_index)
        return attack#self.curr_pos_attack

    """Each turn, pick an item you want to buy. Return Item.None if you don't think you can
    afford anything.

    :param gameState:     A provided GameState object, contains every piece of info on the game board.
    :param myPlayerIndex: You may find out which player on the board you are.

    :returns: A game.Item object.
    """
    @abstractmethod
    def buy_action_decision(self, game_state: GameState, my_player_index: int) -> Item:
        if gold(game_state.player_state_list[my_player_index]) >= 5:
            return Item.SPEED_POTION
        return Item.NONE

#generates all of the possible locations that a player at a given position can go to
def generate_possible_locations(player_state: PlayerState):
    poss_locs = []
    center = player_state.position
    s = speed(player_state)
    for xp in range(max(center.x - s, 0), min(center.x + s + 1, 10)):
        for yp in range(max(center.y - s, 0), min(center.y + s + 1, 10)):
            if manhattan_distance(center, Position(xp, yp)) <= s:
                poss_locs.append(Position(xp, yp))
    return poss_locs


def hits_to_kill_enemy(player_state: PlayerState, enemy_state: PlayerState):
    return math.ceil(hp(enemy_state) / damage(player_state))

def gold(player_state: PlayerState):
    return player_state.gold

def score(player_state: PlayerState):
    return player_state.score

def hp(player_state: PlayerState):
    return player_state.health

def max_hp(player_state: PlayerState):
    return player_state.stat_set.max_health

def damage(player_state: PlayerState):
    return player_state.stat_set.damage

def speed(player_state: PlayerState):
    return player_state.stat_set.speed

def attack_range(player_state: PlayerState):
    return player_state.stat_set.range

def distance_from_center(pos: Position):
    return min(manhattan_distance(pos, Position(4,4)), manhattan_distance(pos, Position(4,5)), manhattan_distance(pos, Position(5,4)), manhattan_distance(pos, Position(5,5)))

def position(player_state: PlayerState):
    return player_state.position

def isInCenter(pos: Position):
    return distance_from_center(pos) == 0

def isOneFromCenter(override_player_pos: Position, player_state: PlayerState):
    return speed(player_state) >= distance_from_center(override_player_pos)
    
def can_attack(player1: PlayerState, player1pos: Position, player2pos: Position):
    p1_range = attack_range(player1)
    return True if chebyshev_distance(player1pos, player2pos) <= p1_range else False

def can_kill(player1: PlayerState, player2: PlayerState):
    return can_attack(player1, player1.position, player2.position) and (hp(player2) - damage(player1) <= 0)

def choosePositionAndAttack(game_state: GameState, my_player_index: int):
    our_state = game_state.player_state_list[my_player_index]
    possible_positions = generate_possible_locations(our_state)
    values = np.zeros(len(possible_positions))
    attacks = np.zeros(len(possible_positions))
    for idx, temp_pos in enumerate(possible_positions):
        value = -distance_from_center(temp_pos)
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
            htk = hits_to_kill_enemy(our_state, enemy_state)
            curr_pos_attack[i] += -htk*damage(our_state) + (hp(enemy_state) - 1) % damage(our_state)
            if can_attack(our_state, our_state.position, enemy_state.position):
                curr_pos_attack[i] += 100
            enemy_moves = generate_possible_locations(enemy_state)
            count_of_center  = 0
            count_of_one_from_center = 0
            count_of_overlap_us = 0
            count_of_overlap_them = 0
            for enemy_move in enemy_moves:
                if isInCenter(enemy_move):
                    count_of_center += 1
                elif isOneFromCenter(enemy_move, enemy_state):
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
            
