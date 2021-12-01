#  (C) Copyright Wieger Wesselink 2021. Distributed under the GPL-3.0-or-later
#  Software License, (See accompanying file LICENSE or copy at
#  https://www.gnu.org/licenses/gpl-3.0.txt)

import random
import time
import math
from typing import List
from competitive_sudoku.sudoku import GameState, Move, SudokuBoard, TabooMove
import competitive_sudoku.sudokuai
from copy import deepcopy

CHECKS = {
    "INVALID": 0,
    "VALID": 1,
    "SCORING": 2
}
SCORES = [0, 1, 3, 7]
DEBUG = False

class Node:
    def __init__(self, game_state, move, our_move):
        self.game_state = game_state
        self.children = []
        self.move = move
        self.our_move = our_move
        self.taboo = False
        self.value = self.calc_value()

    def calc_value(self):
        val = evaluate(self.game_state, self.move)
        if val == -1:
            self.taboo = True
        if not self.our_move:
            val *= -1
        return val

    def add_child(self, node):
        if (node.value == -1):
            return
        self.children.append(node)

    def update_gamestate(self):
            self.game_state.board.put(self.move.j, self.move.i, self.move.value)

    def has_children(self):
        return bool(self.children)

    def get_children(self):
        return self.children


class SudokuAI(competitive_sudoku.sudokuai.SudokuAI):
    """
    Sudoku AI that computes a move for a given sudoku configuration.
    """

    """
    TODO:
        - function to generate all legal moves - DONE
        - evaluation function - DONE
        - ALWAYS have a move proposed (so propose a 'random' move before calculating layers)
        - minimax tree search algorithm to find best move
    """

    def __init__(self):
        self.highest_value = -1
        super().__init__()

    def compute_best_move(self, game_state: GameState) -> None:

        all_moves = self.get_all_moves(game_state)
        player_1 = True
        root_move = Move(0, 0, 0)
        for move in all_moves:
            if evaluate(game_state, move) != -1:
                # We assumed x and y were flipped. To prevent
                # rewriting all the code, we swap them back here.
                self.propose_move(Move(move.j, move.i, move.value))
                break
        root = Node(game_state, root_move, player_1)
        depth = 0

        # First, we need to compute layer 1
        root = self.calculate_children(root, all_moves, player_1)
        depth = depth + 1
        player_1 = not player_1

        # Then, keep computing moves as long as there are
        # moves to make, alternating between
        # friendly moves and hostile moves.

        kids = root.children
        while bool(kids):
            temp_kids = []
            for child in kids:
                child.update_gamestate()
                new_all_moves = self.get_all_moves(child.game_state)
                child = self.calculate_children(child, new_all_moves, player_1)

                for leaf in child.children:
                    temp_kids.append(leaf)
            kids = temp_kids

            depth = depth + 1
            best_move = self.minimax(root, depth, -math.inf, math.inf, True).move
            print(f"best move is:{best_move}")
            self.propose_move(Move(best_move.j, best_move.i, best_move.value))
            print("LAYER FINISHED")
            player_1 = not player_1


    def calculate_children(self, root, all_moves: list, our_move: bool):
        for move in all_moves:
            new_game_state = deepcopy(root.game_state)
            new_move = deepcopy(move)
            #node = Node(new_game_state, evaluate(new_game_state, new_move), new_move)
            node = Node(new_game_state, new_move, our_move)
            if not node.taboo:
                root.add_child(node)
        return root

    def get_all_moves(self, game_state: GameState) -> List[Move]:
        """
        Returns a list of all possible moves
        :param game_state: a game state
        :return: a list of moves
        """
        N = game_state.board.N

        def possible(i, j, value):
            return game_state.board.get(i, j) == SudokuBoard.empty and not TabooMove(i, j, value) in game_state.taboo_moves

        return [Move(i, j, value) for i in range(N) for j in range(N) for value in range(1, N+1) if possible(j, i, value)]

    def debug(self, text):
        if DEBUG:
            print("-" * 25)
            print(text)
            print("-" * 25)

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
        print(f"is_maximising_player is: {is_maximising_player}")
        print(f"depth is: {depth}")

        if is_maximising_player:
            # maxValue = Node(None, -math.inf, None)
            maxValue = deepcopy(node)
            maxValue.value = -math.inf
            for child in children:
                print(f"proposed child move: {child.move}")
                value = self.minimax(child, depth - 1, alpha, beta, False)
                print(f"value_move:{value.move}, maxValue_move:{maxValue.move}, value: {value.value}, maxValue: {maxValue.value}, alpha: {alpha}, beta: {beta}")
                maxValue = max([maxValue, value], key=lambda state: state.value)
                alpha = max(maxValue.value, alpha)
                print(f"value_move:{value.move}, maxValue_move:{maxValue.move}, value: {value.value}, maxValue: {maxValue.value}, alpha: {alpha}, beta: {beta}")
                # if beta <= alpha:
                #     print("beta is less or equal to alpha")
                #     break
            return maxValue
        else:
            # minValue = Node(None, math.inf, None)
            minValue = deepcopy(node)
            minValue.value = math.inf
            for child in children:
                value = self.minimax(child, depth - 1, alpha, beta, True)
                print(f"value_move:{value.move}, minValue_move:{minValue.move}, value: {value.value}, minValue: {minValue.value}, alpha: {alpha}, beta: {beta}")
                minValue = min([minValue, value], key=lambda state: state.value)
                beta = min(minValue.value, beta)
                print(f"value_move:{value.move}, minValue_move:{minValue.move}, value: {value.value}, minValue: {minValue.value}, alpha: {alpha}, beta: {beta}")
                # if beta <= alpha:
                #     print("beta is less or equal to alpha")
                #     break
            return minValue


def evaluate(game_state: GameState, move: Move):
    """
    Evaluates a single move and returns a score
    :param game_state: a game state
    :param move: a move
    :return: score
    """
    scores = 0
    col = check_column(game_state, move)
    if col == CHECKS["INVALID"]:
        return -1
    else:
        if col == CHECKS["SCORING"]:
            scores += 1
        row = check_row(game_state, move)
        if row == CHECKS["INVALID"]:
            return -1
        else:
            if row == CHECKS["SCORING"]:
                scores += 1
            square = check_square(game_state, move)
            if square == CHECKS["INVALID"]:
                return -1
            else:
                if square == CHECKS["SCORING"]:
                    scores += 1
    return SCORES[scores]

def check_row(game_state: GameState, move: Move):
    """
        Checks if all cells in a row are filled for a given move.
        Returns:
            0       invalid move
            1       valid move
            2       scoring move
    """
    index = move.j
    values = []
    valid = False
    for i in range(game_state.board.N):
        # i == move.j : CORRECT
        if i == move.i:
            pass
        elif (game_state.board.get(index, i) != 0):
            values.append(game_state.board.get(index, i))
        else:
            valid = True
    if move.value in values:
        return CHECKS["INVALID"]
    elif valid:
        return CHECKS["VALID"]
    return CHECKS["SCORING"]

def check_column(game_state: GameState, move: Move):
    """
        Checks if all cells in a column are filled for a given move.
        Returns:
            0       invalid move
            1       valid move
            2       scoring move
    """
    index = move.i
    values = []
    valid = False
    for k in range(game_state.board.N):
        # k == move.i : CORRECT
        if k == move.j:
            pass
        elif (game_state.board.get(k, index) != 0):
            values.append(game_state.board.get(k, index))
        else:
            valid = True
    if move.value in values:
        return CHECKS["INVALID"]
    elif valid:
        return CHECKS["VALID"]
    return CHECKS["SCORING"]

def check_square(game_state: GameState, move: Move):
    """
        Checks if all cells in a square are filled for a given move.
        Returns:
            0       invalid move
            1       valid move
            2       scoring move
    """
    values = []
    m = game_state.board.m
    n = game_state.board.n
    column = move.i // m
    row = move.j // n
    valid = False
    # iterate over each row
    for i in range(m):
        # then each column
        for j in range(n):
            curr = game_state.board.get(m * row + i, n * column + j)
            # Do we have an empty cell?
            if curr == 0:
                # Is this empty cell the move we currently want to make?
                if m * row + i == move.j and n * column + j == move.i:
                    pass
                else:
                    valid = True
            else:
                values.append(curr)
    if move.value in values:
        return CHECKS["INVALID"]
    elif valid:
        return CHECKS["VALID"]
    return CHECKS["SCORING"]