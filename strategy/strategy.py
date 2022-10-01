from abc import abstractmethod
from game.game_state import GameState
from game.item import Item
from game.player_state import PlayerState
from game.position import Position
from util.utility import manhattan_distance, chebyshev_distance
import math

class Strategy(object):
    """Before the game starts, pick a class for your bot to start with.

    :returns: A game.CharacterClass Enum.
    """
    @abstractmethod
    def strategy_initialize(self, my_player_index: int) -> None:
        self.index = my_player_index
        self.curr_action = Position(0,0)
        self.curr_attack = 0

    """Each turn, decide if you should use the item you're holding. Do not try to use the
    legendary Item.None!

    :param gameState:     A provided GameState object, contains every piece of info on the game board.
    :param myPlayerIndex: You may find out which player on the board you are.

    :returns: If you want to use your item
    """
    @abstractmethod
    def use_action_decision(self, game_state: GameState, my_player_index: int) -> bool:
        position, attack = choosePositionAndAttack(game_state, my_player_index)
        self.curr_action = position
        self.curr_attack = attack
        pass

    """Each turn, pick a position on the board that you want to move towards. Be careful not to
    fall out of the board!

    :param gameState:     A provided GameState object, contains every piece of info on the game board.
    :param myPlayerIndex: You may find out which player on the board you are.

    :returns: A game.Position object.
    """
    @abstractmethod
    def move_action_decision(self, game_state: GameState, my_player_index: int) -> Position:
        our_player = game_state.player_state_list[my_player_index]
        our_player.position = self.curr_action
        return self.curr_action

    """Each turn, pick a player you would like to attack. Feel free to be a pacifist and attack no
    one but yourself.

    :param gameState:     A provided GameState object, contains every piece of info on the game board.
    :param myPlayerIndex: You may find out which player on the board you are.

    :returns: Your target's player index.
    """
    @abstractmethod
    def attack_action_decision(self, game_state: GameState, my_player_index: int) -> int:
        return self.curr_attack

    """Each turn, pick an item you want to buy. Return Item.None if you don't think you can
    afford anything.

    :param gameState:     A provided GameState object, contains every piece of info on the game board.
    :param myPlayerIndex: You may find out which player on the board you are.

    :returns: A game.Item object.
    """
    @abstractmethod
    def buy_action_decision(self, game_state: GameState, my_player_index: int) -> Item:
        pass

def generate_possible_locations(player_state: PlayerState):
    poss_locs = []
    center = player_state.position
    s = speed(player_state)
    for x in range(max(center.x - s), min(center.x + s + 1, 10)):
        for y in range(max(center.x - s), min(center.y + s + 1, 10)):
            if manhattan_distance(center, Position(x, y)) <= s:
                poss_locs.append(Position(x, y))
    return poss_locs


def hits_to_kill_enemy(player_state: PlayerState, enemy_state: PlayerState):
    return math.ceil(hp(enemy_state) / damage(player_state))

def hp(player_state: PlayerState):
    return player_state.health

def max_hp(player_state: PlayerState):
    return player_state.stat_set.max_health

def damage(player_state: PlayerState):
    return player_state.stat_set.damage

def speed(player_state: PlayerState):
    return player_state.stat_set.speed

def range(player_state: PlayerState):
    return player_state.stat_set.range

def distance_from_center(pos: Position):
    return min(manhattan_distance(pos, Position(4,4)), manhattan_distance(pos, Position(4,5)), manhattan_distance(pos, Position(5,4)), manhattan_distance(pos, Position(5,5)))

def position(player_state: PlayerState):
    return player_state.position

def isInCenter(pos: Position):
    return distance_from_center == 0
def isOneFromCenter(player_state: PlayerState):
    if isInCenter(player_state.position):
        return True
    positions = generate_possible_locations(player_state)
    for pos in positions:
        if isInCenter(pos):
            return True
    return False
    
def can_attack(player1: PlayerState, player1pos: Position, player2pos: Position):
    p1_speed = speed(player1)
    return True if chebyshev_distance(player1pos, player2pos) <= p1_speed else False

def can_kill(player1: PlayerState, player2: PlayerState):
    return can_attack(player1, player1.position, player2.position) and (hp(player2) - player1.stat_set.damage <= 0)

def choosePositionAndAttack(game_state: GameState, my_player_index: int):
    our_state = game_state.player_state_list[my_player_index]
    possible_positions = generate_possible_locations(our_state.position)
    values = []
    attacks = []
    for pos in possible_positions:
        value = 0
        value -= distance_from_center(pos)
        values.append((pos,value))
    max_val = -100000
    max_index = 0
    for i in range(len(values)):
        if values[i][1] > max_val:
            max_val = values[i][1]
            max_index = i
    best_pos = values[max_index][0]
    best_attack = attacks[max_index]
    return (best_pos, best_attack)
            
