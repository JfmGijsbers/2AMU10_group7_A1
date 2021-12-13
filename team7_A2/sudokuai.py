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
from team7_A2.strategies import only_choice
from copy import deepcopy
import logging
import sys

log = logging.getLogger("sudokuai")
log.setLevel(logging.DEBUG)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.CRITICAL)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
log.addHandler(handler)


class SudokuAI(competitive_sudoku.sudokuai.SudokuAI):
    """
    Sudoku AI that computes a move for a given sudoku configuration.
    """

    def __init__(self):
        self.highest_value = -1
        super().__init__()

    
    def pick_strategy(self, game_state: GameState, our_move):
        if our_move:
            return only_choice(game_state)
        else:
            return get_all_moves(game_state)

    def compute_best_move(self, game_state: GameState) -> None:

        our_move = True
        all_moves = self.pick_strategy(game_state, our_move)
        if len(all_moves) == 0:
            log.error("No moves found!")
        # Always have a move proposed
        try:
            self.propose_move(all_moves[0])
        except:
            log.critical("Not proposing any moves")
            return
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
        #our_move = not our_move
        our_move = not our_move
        root.update_gamestate()
 
        # Then, keep computing moves as long as there are
        # moves to make, alternating between
        # friendly moves and hostile moves.

        kids = root.children
        while len(kids) != 0:
            temp_kids = []
            for child in kids:
                child.update_gamestate()
                new_all_moves = self.pick_strategy(child.game_state, our_move)
                child.calculate_children(child, new_all_moves, our_move)

                for leaf in child.children:
                    temp_kids.append(leaf)
            kids = temp_kids
            log.info(f"Found {len(temp_kids)} moves for {'us' if our_move else 'them'} ")

            depth += 1
            # If the last turn is not ours,
            # we don't want to run the minimax for this turn
            if len(kids) == 0:
                log.critical("Last turn, stop minimaxing")
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
            # maxValue = Node(None, -math.inf, None)
            maxValue = deepcopy(node)
            maxValue.value = -math.inf
            #print(f"{node.move}")
            #print(f"{len(children)} children")
            for child in children:
                #print(f"proposed child move: {child.move}")
                value = self.minimax(child, depth - 1, alpha, beta, False)
                #print(f"value_move:{value.move}, maxValue_move:{maxValue.move}, value: {value.value}, maxValue: {maxValue.value}, alpha: {alpha}, beta: {beta}")
                maxValue = max([maxValue, value], key=lambda state: state.value)
                alpha = max(maxValue.value, alpha)
                #print(f"value_move:{value.move}, maxValue_move:{maxValue.move}, value: {value.value}, maxValue: {maxValue.value}, alpha: {alpha}, beta: {beta}")
                if beta <= alpha:
                    #print("beta is less or equal to alpha")
                    break
            return maxValue
        else:
            # minValue = Node(None, math.inf, None)
            minValue = deepcopy(node)
            minValue.value = math.inf
            for child in children:
                value = self.minimax(child, depth - 1, alpha, beta, True)
                #print(f"value_move:{value.move}, minValue_move:{minValue.move}, value: {value.value}, minValue: {minValue.value}, alpha: {alpha}, beta: {beta}")
                minValue = min([minValue, value], key=lambda state: state.value)
                beta = min(minValue.value, beta)
                #print(f"value_move:{value.move}, minValue_move:{minValue.move}, value: {value.value}, minValue: {minValue.value}, alpha: {alpha}, beta: {beta}")
                if beta <= alpha:
                    #print("beta is less or equal to alpha")
                    break
            return minValue