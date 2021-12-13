#  (C) Copyright Wieger Wesselink 2021. Distributed under the GPL-3.0-or-later
#  Software License, (See accompanying file LICENSE or copy at
#  https://www.gnu.org/licenses/gpl-3.0.txt)

import random
import time
import math
from typing import List
from competitive_sudoku.sudoku import GameState, Move, SudokuBoard, TabooMove
import competitive_sudoku.sudokuai
from team7_A2.evaluate import evaluate, get_all_moves
from team7_A2.node import Node
from copy import deepcopy

import logging
log = logging.getLogger("sudokuai")

class SudokuAI(competitive_sudoku.sudokuai.SudokuAI):
    """
    Sudoku AI that computes a move for a given sudoku configuration.
    """

    def __init__(self):
        self.highest_value = -1
        super().__init__()

    def compute_best_move(self, game_state: GameState) -> None:

        all_moves = get_all_moves(game_state)
        if len(all_moves) == 0:
            log.error("No moves found!")
        # Always have a move proposed
        try:
            self.propose_move(all_moves[0])
        except:
            log.error("Not proposing any moves")
            return
        # When this function is called, it is always
        # our turn
        our_move = True
        root_move = Move(0, 0, 0)
        move = random.choice(all_moves)
        # To make the always proposed move a bit more random (better performance)
        # just sample a random legal move
        while evaluate(game_state, move) == -1:
            move = random.choice(all_moves)
        log.info(f"Proposing move {move}")
        self.propose_move(move)
        log.info(f"Proposed move {move}")
        root = Node(game_state, root_move, our_move)
        depth = 0

        # First, we need to compute layer 1
        root.calculate_children(root, all_moves, our_move)
        depth += 1
        best_move = self.minimax(root, depth, -math.inf, math.inf, our_move).move
        log.info(f"Found best move: {str(best_move)}")
        self.propose_move(best_move)
        our_move = not our_move
 
        # Then, keep computing moves as long as there are
        # moves to make, alternating between
        # friendly moves and hostile moves.

        kids = root.children
        while len(kids) != 0:
            temp_kids = []
            for child in kids:
                child.update_gamestate()
                new_all_moves = get_all_moves(child.game_state)
                child.calculate_children(child, new_all_moves, our_move)

                for leaf in child.children:
                    temp_kids.append(leaf)
            kids = temp_kids

            depth += 1
            # If the last turn is not ours,
            # we don't want to run the minimax for this turn
            log.info(f"Length {len(temp_kids)} and our_move is {our_move}")
            if len(kids) == 0:
                log.info("Last turn, stop minimaxing")
            else:
                best_move = self.minimax(root, depth, -math.inf, math.inf, our_move).move
                log.info(f"Ran depth {depth}, proposing {best_move}")
                self.propose_move(best_move)
            our_move = not our_move


    def minimax(self, node, depth, alpha, beta, is_maximising_player) -> Node:
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