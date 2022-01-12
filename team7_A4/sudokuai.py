#  (C) Copyright Wieger Wesselink 2021. Distributed under the GPL-3.0-or-later
#  Software License, (See accompanying file LICENSE or copy at
#  https://www.gnu.org/licenses/gpl-3.0.txt)

import random
import math
from typing import Union, Tuple, List
from competitive_sudoku.sudoku import GameState, Move
import competitive_sudoku.sudokuai
from .node import Node
from .evaluation import get_all_moves, get_strategy
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
        saved_data = None
        # Load data if data is available
        saved_data = self.load()
        saved_data = self.update_saved_data(saved_data, GameState)

        # Determine which strategies to play
        strategies = get_strategy(saved_data)

        # Calculate the first layer of moves depending on the given strategies
        nont_moves, maybet_moves, t_moves = get_all_moves(saved_data, strategies)

        # Save data
        self.save(saved_data)

        # Initialize all trees
        all_trees = []
        for i, data_move in enumerate(data_moves):
            all_trees.append(Node(data_move, True))
        # sort trees on priority
        all_trees.sort(key=lambda game_tree: game_tree.priority)
        self.propose_best_move(all_trees)

        # # ITERATIVE DEEPENING
        # # Keep computing moves as long as there are moves to make,
        # # alternating between our and the opponent's turn
        # leaves = []
        # while leaves:
        #     # for all trees
        #     # TODO decide on priority
        #     # check layer up
        #     for leaf in leaves:
        #         # Calculate the first layer of moves depending on the given strategies
        #         leaf.add_layer() #add children to leaves if possible, calc value
        #         if not leaf.is_leaf():
        #             best_move = self.minimax(tree, tree.depth, -math.inf, math.inf, False)
        #
        #     # calculate best move
        #     if len(children) != 0:
        #         best_move = self.minimax(root, depth, -math.inf, math.inf, False)
        #         self.propose_move(best_move.root_move)
        #         print(f"finished layer {depth}")
        #     else:
        #         print("FINISHED TREE")

    def minimax(self, node: Node, depth: int, alpha: Union[float, int], beta: Union[float, int],
                is_maximising_player: bool) -> Tuple[Node, int]:
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
        if depth == 0:
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
