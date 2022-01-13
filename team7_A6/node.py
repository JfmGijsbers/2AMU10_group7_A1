from __future__ import annotations
from competitive_sudoku.sudoku import GameState, Move
from .evaluate import evaluate_val
from copy import deepcopy
from typing import List, Union
import logging
from .timer import Timer
import math

logger = logging.getLogger("sudokuaiA3")
logger.setLevel(logging.DEBUG)

PRIORITY_N = 4

class Node:
    def __init__(self, parent_game_state: GameState = None,
                 move: Move = None,
                 is_maximising_player: bool = None,
                 depth: int = None,
                 is_dummy: int = 0):
        """
        a Node object is part of the game tree
        each layer of the game tree represents a turn
        a node has:
            * root_move: first next move played by the maximising player of this game tree
            * depth: depth of this node
            * move: move of this node
            * parent_game_state: game state of parent node
            * game_state: game state of this node
            * children: list of calculated children
            * is_maximising_player: is it the turn of the maximising player
            * taboo: is move a taboo move?
            * value: gained value of the move
        :param parent_game_state: Parent game state
        :param move: New move
        :param is_maximising_player: Is it the maximising player's turn?
        :param depth: Depth of the node in the game tree
        """
        if is_dummy == 0:
            self.root_move = (0, 0, 0)
            self.depth = depth
            self.move = move
            self.parent_game_state = parent_game_state
            self.taboo = False
            self.game_state = self.update_gamestate(self.parent_game_state)
            self.children = []
            self.is_maximising_player = is_maximising_player
            val, priority = self.calc_value()
            self.value = val
            self.score = 0
            self.priority = priority
        elif is_dummy == 1:
            self.score = -math.inf
            self.value = -math.inf
        elif is_dummy == 2:
            self.score = math.inf
            self.value = math.inf

    #
    # @Timer(name="calculate_val", text="calculate_val - elapsed time - {:0.4f} seconds")
    def calc_value(self):
        """
        Calculates the gained value of the move
        note: values of the minimising player are negative
        :return: gained value of the move
        """
        if self.depth == 0:
            val = 0
            priority = 10
        else:
            with Timer(name="evaluate", text="evaluate - elapsed time - {:0.4f} seconds", logger=None):
                val, priority = evaluate_val(self.parent_game_state.board, self.move)
        if not self.is_maximising_player and self.depth != 0:
            val *= -1
        return val, priority

    def add_child(self, child: Node) -> None:
        """
        adds a child to the node
        :param child: child to add
        :return: updates the children list of the node
        """
        self.children.append(child)

    # @Timer(name="calculate_children", text="calculate_children - elapsed time - {:0.4f} seconds")
    def calculate_children(self, cand_moves: list, with_priority: bool) -> List[Move]:
        """
        Calculates and adds all non-taboo candidate moves
        by making nodes of the moves which
            * calculates the score
            * checks if it's a taboo move
        :param cand_moves: list of candidate moves for the children
        :return: updates the children list of the node
        """
        low_priority = []
        for cand_move in cand_moves:
            with Timer(name="maken van een Node", text="making a node - elapsed time - {:0.4f} seconds", logger=None):
                node = Node(self.game_state, cand_move, not self.is_maximising_player, self.depth + 1)
            if not node.taboo:
                # ROOT NODE
                if self.depth == 0:
                    node.root_move = cand_move
                else:
                    node.root_move = self.root_move

                # PRIORITY
                if node.priority <= PRIORITY_N and with_priority:
                    self.add_child(node)
                elif not with_priority:
                    self.add_child(node)
                else:
                    low_priority.append(node.move)
        return low_priority

    def update_gamestate(self, parent_game_state: GameState) -> GameState:
        """
        Updates the old game state with the proposed move of the Node
        :param parent_game_state: previous game state
        :return: new game state after proposed move
        """
        game_state = deepcopy(parent_game_state)
        if self.depth != 0 and not self.taboo:
            game_state.board.put(self.move.i, self.move.j, self.move.value)
            game_state.moves.append(self.move)
        return game_state

    def has_children(self) -> bool:
        """
        Returns a boolean on whether the Node has any children
        :return: boolean
        """
        return bool(self.children)

    def get_children(self) -> List[Node]:
        """
        Returns a list with Node children of the Node
        :return: a list with Node children
        """
        return self.children

    def add_score(self, score: Union[float, int]) -> None:
        self.score = score
