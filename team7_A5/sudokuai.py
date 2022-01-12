#  (C) Copyright Wieger Wesselink 2021. Distributed under the GPL-3.0-or-later
#  Software License, (See accompanying file LICENSE or copy at
#  https://www.gnu.org/licenses/gpl-3.0.txt)

import random
import math
from typing import Union, Tuple, List
from competitive_sudoku.sudoku import GameState, Move
import competitive_sudoku.sudokuai
from .node import Node, MoveData
from .calc_moves import get_all_moves, get_strategy
from .evaluation import evaluate, get_move_data
from copy import deepcopy
import logging
import numpy as np

log = logging.getLogger("sudokuai")


class SudokuAI(competitive_sudoku.sudokuai.SudokuAI):
    """
    Sudoku AI that computes a move for a given sudoku configuration.
    """

    # TODO prioritise -> Yi He 2e
    # TODO skip turn -> Yi He 1e
    # TODO strategies -> 5e
    # TODO pick strategies depending on the game state phase
    # TODO horizontale random choice fixen (in minimax door de min en max) -> Yi He
    # TODO snelle agent -> Jeroen
    # TODO optimaliseren (sneller) gebruik van eerder gemaakte variablen bij andere functies -> Yi He 3e
    # TODO save load -> Yi He 4e
    # TODO verslag -> Sander
    # TODO code anderen -> Sander

    def __init__(self):
        super().__init__()

    def compute_best_move(self, game_state: GameState) -> None:
        """
        Computes the best move
        definitions:
        * Legal move: A move that corresponds with the rules of the sudoku
        * Taboo move: A legal move that will result in an unsolvable sudoku
        * Unit: row, column or box

        :param game_state: the game_state
        :return:
        """
        # saved_data = None
        # # Load data if data is available
        # saved_data = self.load()
        # if saved_data is None:
        #
        # else:
        #     saved_data = self.update_saved_data(saved_data, GameState)

        # Calculate the initial score
        player_num = game_state.current_player()
        if player_num == 1:
            init_score = game_state.scores[1] - game_state.scores[0]
        else:
            init_score = game_state.scores[0] - game_state.scores[1]

        # Calculate the first layer of moves depending on the given strategies
        all_moves, legal_moves, maybet_moves, t_moves = get_all_moves(game_state.board, game_state.taboo_moves)
        # # Save data
        # self.save(saved_data)

        # propose move
        self.propose_move(random.choice(all_moves))

        # all_moves.sort(key=lambda moves: moves.priority)
        # self.propose_best_move(legal_moves)

        # Now we start doing search tree stuff and offering a new move every depth
        root = Node(MoveData(value=init_score, board=game_state.board, taboo_moves=game_state.taboo_moves))
        if bool(legal_moves):
            to_add = get_move_data(legal_moves)
            root.minimax(t_moves, to_add)
        to_add = get_move_data(maybet_moves)
        root.minimax(t_moves, to_add)

        # while True:
        #     # Extend the depth of the trees by 1
        #     search_tree.add_layer(legal_moves, maybet_moves, t_moves)
        #
        #     # Return best move in tree for current depth
        #     best_move = find_best_move(search_tree)
        #     self.propose_move(best_move)

    def minimax(self, node: Node, alpha: Union[float, int], beta: Union[float, int],
                is_maximising_player: bool) -> Node:
        """
        Recursively evaluates nodes in game tree and returns the proposed best node.
        Proposed best node is the node that has either the maximum or the mimimum value in the terminal state
        depending if is_maximising_player is True or False respectively.
        :param node: starting state
        :param depth: terminal search depth
        :param alpha: pruning
        :param beta: pruning
        :param is_maximising_player: is maximising player?
        :param score: current score
        :return: best node proposal
        """
        if node.is_leaf():
            node.add_score(node.value)
            return node

        children = node.children
        if is_maximising_player:
            # deep copy node, since it has to be a node object to compare
            maxValue = deepcopy(node)
            maxValue.add_score(-math.inf)
            # assign -inf value to the node
            for child in children:
                if node.depth == 0:
                    value = self.minimax(child, depth - 1, alpha, beta, True)
                else:
                    value = self.minimax(child, depth - 1, alpha, beta, False)
                random_boolean = bool(random.getrandbits(1))
                if random_boolean:
                    maxValue = max([maxValue, value], key=lambda state: state.score)
                else:
                    maxValue = max([value, maxValue], key=lambda state: state.score)
                alpha = max(maxValue.score, alpha)
                if beta <= alpha:
                    break
            maxValue.add_score(maxValue.score + node.value)
            return maxValue
        else:
            # minimizing player, similar to the maximising player
            minValue = deepcopy(node)
            minValue.add_score(math.inf)
            for child in children:
                value = self.minimax(child, depth - 1, alpha, beta, True)
                random_boolean = bool(random.getrandbits(1))
                if random_boolean:
                    minValue = min([minValue, value], key=lambda state: state.score)
                else:
                    minValue = min([value, minValue], key=lambda state: state.score)
                beta = min(minValue.score, beta)
                if beta <= alpha:
                    break
            minValue.add_score(minValue.score + node.value)
            return minValue

    def propose_best_move(self, moves: List[Node]) -> None:
        """
        moves contains a list with all Node of the first move that can be played
        Node has a score, which represents the maximum score it can get playing that move
        :param moves:
        :return:
        """
        max_score = max(moves, key=lambda move: move.score)
        max_moves = [move for move in moves if move.score == max_score]
        move = random.choice(max_moves)
        self.propose_move(move.root)

    def update_saved_data(self):
        pass
