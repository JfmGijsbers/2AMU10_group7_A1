#  (C) Copyright Wieger Wesselink 2021. Distributed under the GPL-3.0-or-later
#  Software License, (See accompanying file LICENSE or copy at
#  https://www.gnu.org/licenses/gpl-3.0.txt)

import random
import math
from typing import Union, Tuple, List
from competitive_sudoku.sudoku import GameState, Move
import competitive_sudoku.sudokuai
from .evaluate import evaluate_val
from .node import Node
from .strat import get_all_moves, get_strategy
from copy import deepcopy
import logging
import time
from .timer import Timer

# LOGGER SETTINGS
logger = logging.getLogger("sudokuaiA3")
logger.setLevel(logging.INFO)

fh = logging.FileHandler('timing.txt')
fh.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)

# add the handlers to the logger
logger.addHandler(fh)
logger.addHandler(ch)


class SudokuAI(competitive_sudoku.sudokuai.SudokuAI):
    """
    Sudoku AI that computes a move for a given sudoku configuration.
    Team7_A6 improves on team7_A3 by only adding important nodes to the game tree (with 4 or less empty cells)
    If only the first layer is reached, don't choose a move with priority 2! (which means 2 empty cells)
    When the score is negative, it will choose a move that is either a taboo_move if possible
    """

    def __init__(self):
        super().__init__()

    def compute_best_move(self, game_state: GameState) -> None:
        """
        Computes the best move
        :param game_state: the game_state
        :return:
        """
        logger.info("starting compute_best_move")
        with Timer(name="Making root", text="Making root - {:0.4f} seconds", logger=logger.debug):
            # Instantiate the root of the game tree
            root_move = Move(0, 0, 0)
            depth = 0
            root = Node(game_state, root_move, False, depth)

        # Compute layer 1 by calculating the children of the root
        with Timer(name="Calculate layer 1", text="Calculate layer 1 - {:0.4f} seconds", logger=logger.debug):
            depth = depth + 1
            # Calculate the first layer of moves depending on the given strategies
            # Determine which strategies to play
            strategies = get_strategy(game_state)
            all_moves, taboo_list = get_all_moves(game_state, strategies)
            assert bool(all_moves), "No moves found in layer 1!"
            # Always have a move proposed
            self.propose_move(random.choice(all_moves))
            # CALCULATE CHILDREN
            low_priority = root.calculate_children(all_moves, with_priority=True)
            if not bool(root.children):
                _ = root.calculate_children(all_moves, with_priority=False)
            elif not taboo_list:
                taboo_list = low_priority
            # ACT LIKE THE GREEDY PLAYER
            root.children.sort(key=lambda move: move.priority)
            if root.children[0].priority == 1:
                self.propose_move(root.children[0].move)
            # MINIMAX
            best_move = self.minimax(root, depth, -math.inf, math.inf, False)
            # DON'T PROPOSE A PRIORITY 2 MOVE IF SCORE = 0
            if best_move.score == 0 and root.children[-1].priority != 2:
                self.propose_move(root.children[-1].move)
            elif best_move.score == 0 and root.children[-1].priority == 2:
                if bool(taboo_list):
                    self.propose_move(random.choice(taboo_list))
                elif bool(low_priority):
                    self.propose_move(random.choice(low_priority))
                else:
                    self.propose_move(best_move.root_move)
            else:
                self.propose_move(best_move.root_move)
            # # PROPOSE A TABOO MOVE IF POSSIBLE IF SCORE IS <0
            # elif best_move.score < 0 and bool(taboo_list):
            #     self.propose_taboo(taboo_list)
            logger.info(f"Best move {best_move.root_move} score is {best_move.score}")
            logger.info(f"FINISHED LAYER 1")
        # ITERATIVE DEEPENING
        # Keep computing moves as long as there are moves to make,
        # alternating between our and the opponent's turn
        children = root.children
        while len(children) != 0:
            leaves = []
            depth += 1
            # calculate new layer
            logger.debug(f"Calculate children layer {depth}")
            with Timer(name="children_depth", text="children_depth - {:0.4f} seconds", logger=None):
                for child in children:
                    logger.debug(f"Calculate children layer {depth} for child {child.move}")
                    strategies = get_strategy(game_state)
                    all_moves, _ = get_all_moves(game_state, strategies)
                    # CALCULATE CHILDREN
                    low_priority = root.calculate_children(all_moves, with_priority=True)
                    if not bool(root.children):
                        _ = root.calculate_children(all_moves, with_priority=False)
                    logger.debug(f"Calculated children layer {depth} for child {child.move}")
                    for leaf in child.children:
                        leaves.append(leaf)
            logger.debug(f"Calculated children layer {depth}")
            children = leaves
            random.shuffle(children)
            # calculate best move
            if len(children) != 0:
                logger.debug(f"minimax {depth}")
                with Timer(name="minimax", text="minimax - {:0.4f} seconds", logger=None):
                    # MINIMAX
                    best_move = self.minimax(root, depth, -math.inf, math.inf, False)
                    # PROPOSE A TABOO MOVE IF POSSIBLE IF SCORE IS <0
                    if best_move.score < 0 and bool(taboo_list):
                        self.propose_taboo(taboo_list)
                        logger.info(f"Best move {best_move.root_move} score is {best_move.score}, so I play a taboo move")
                    else:
                        self.propose_move(best_move.root_move)
                        logger.info(f"Best move {best_move.root_move} score is {best_move.score}")
                    logger.info(f"FINISHED LAYER {depth}")
                logger.debug(f"minimaxed {depth}")
            else:
                print("FINISHED TREE")

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
        if is_maximising_player or node.depth == 0:
            # deep copy node, since it has to be a node object to compare
            with Timer(name="minimax copy", text="minimax copy - elapsed time - {:0.4f} seconds", logger=None):
                maxValue = Node(is_dummy=1)
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
            minValue = Node(is_dummy=2)
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

    def propose_taboo(self, taboo_list: List[Move]):
        TAB_MOVE = random.choice(taboo_list)
        self.propose_move(TAB_MOVE)
        logger.info("TABOO MOVE PLAYED")
        print(f"PLAYED A TABOO MOVE {TAB_MOVE}")


