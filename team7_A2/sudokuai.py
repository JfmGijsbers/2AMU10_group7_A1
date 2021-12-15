#  (C) Copyright Wieger Wesselink 2021. Distributed under the GPL-3.0-or-later
#  Software License, (See accompanying file LICENSE or copy at
#  https://www.gnu.org/licenses/gpl-3.0.txt)

import random
import math
from typing import  Union
from competitive_sudoku.sudoku import GameState, Move, SudokuBoard, TabooMove
import competitive_sudoku.sudokuai
from team7_A2.evaluate import evaluate
from team7_A2.node import Node
from team7_A2.strategies import get_all_moves, get_strategy
from copy import deepcopy
import logging

log = logging.getLogger("sudokuai")
log.setLevel(logging.DEBUG)

# handler = logging.StreamHandler(sys.stdout)
# handler.setLevel(logging.CRITICAL)
# formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# handler.setFormatter(formatter)
# log.addHandler(handler)


class SudokuAI(competitive_sudoku.sudokuai.SudokuAI):
    """
    Sudoku AI that computes a move for a given sudoku configuration.
    """

    def __init__(self):
        super().__init__()

    def pick_strategy(self, game_state: GameState, our_move):
        """

        :param game_state:
        :param our_move:
        :return:
        """
        return get_strategy(game_state)

    def compute_best_move(self, game_state: GameState) -> None:
        """
        Computes the best move
        :param game_state:
        :return:
        """
        our_turn = True
        # determine which strategies
        strategies = get_strategy(game_state)
        all_moves = get_all_moves(game_state, strategies)
        if len(all_moves) == 0:
            log.error("No moves found!")

        # Always have a move proposed
        try:
            self.propose_move(all_moves[0])
        except:
            log.critical("Not proposing any moves")
            return
        move = random.choice(all_moves)

        # To make the always proposed move a bit more random (better performance)
        # just sample a random legal move
        while evaluate(game_state, move) == -1:
            move = random.choice(all_moves)
        log.info(f"Proposing move {move}")
        self.propose_move(move)
        log.info(f"Proposed move {move}")

        root_move = Move(0, 0, 0)
        root = Node(game_state, root_move, our_turn)
        depth = 0

        # First, we need to compute layer 1
        depth = depth + 1
        root.calculate_children(root, all_moves, our_turn, depth)
        best_move = self.minimax(root, depth, -math.inf, math.inf, our_turn)
        log.info(f"Found best move: {str(best_move.root_move)}")

        self.propose_move(best_move.root_move)
        our_turn = not our_turn
 
        # Then, keep computing moves as long as there are
        # moves to make, alternating between
        # friendly moves and hostile moves.
        kids = root.children
        while len(kids) != 0:
            temp_kids = []
            depth += 1
            for child in kids:
                strategies = get_strategy(child.new_game_state)
                new_all_moves = get_all_moves(child.new_game_state, strategies)
                child.calculate_children(child, new_all_moves, our_turn, depth)

                for leaf in child.children:
                    temp_kids.append(leaf)
            kids = temp_kids
            log.info(f"Found {len(temp_kids)} moves for {'us' if our_turn else 'them'} ")

            # If the last turn is not ours,
            # we don't want to run the minimax for this turn
            if len(kids) == 0:
                log.critical("Last turn, stop minimaxing")
            else:
                best_move = self.minimax(root, depth, -math.inf, math.inf, our_turn)
                log.info(f"Ran depth {depth}, proposing {best_move.root_move}")
                self.propose_move(best_move.root_move)
            our_turn = not our_turn

    def minimax(self, node: Node, depth: int, alpha: Union[float, int], beta: Union[float, int],
                is_maximising_player: bool) -> Node:
        """
        Recursively evaluates nodes in game tree and returns the proposed best node
        proposed best node is the node that has either the maximum or the mimimum value in the terminal state
        depending on is_maximising_player True or False respectively
        :param node: starting state
        :param depth: terminal search depth
        :param alpha: pruning
        :param beta: pruning
        :param is_maximising_player: is maximising player?
        :return: best node proposal
        """
        if depth == 0 or not node.has_children:
            return node

        children = node.children
        if is_maximising_player:
            # deep copy node, since it has to be a node object to compare
            maxValue = deepcopy(node)
            # assign -inf value to the node
            maxValue.value = -math.inf
            for child in children:
                value = self.minimax(child, depth - 1, alpha, beta, False)
                maxValue = max([maxValue, value], key=lambda state: state.value)
                alpha = max(maxValue.value, alpha)
                if beta <= alpha:
                    break
            return maxValue
        else:
            # minimizing player, similar to the maximising player
            minValue = deepcopy(node)
            minValue.value = math.inf
            for child in children:
                value = self.minimax(child, depth - 1, alpha, beta, True)
                minValue = min([minValue, value], key=lambda state: state.value)
                beta = min(minValue.value, beta)
                if beta <= alpha:
                    break
            return minValue