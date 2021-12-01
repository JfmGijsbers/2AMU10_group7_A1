#  (C) Copyright Wieger Wesselink 2021. Distributed under the GPL-3.0-or-later
#  Software License, (See accompanying file LICENSE or copy at
#  https://www.gnu.org/licenses/gpl-3.0.txt)

import random
import time
import math
from typing import List
from competitive_sudoku.sudoku import GameState, Move, SudokuBoard, TabooMove
import competitive_sudoku.sudokuai

CHECKS = {
    "INVALID": 0,
    "VALID": 1,
    "SCORING": 2
}
SCORES = [0, 1, 3, 7]
DEBUG = False


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
        N = game_state.board.N

        all_moves = self.get_all_moves(game_state)
        root_move = Move(0, 0, 0)
        root = Node(game_state, 0, [], root_move)

        # LOOP: change our_move
        self.calculate_layer(root, all_moves, True)
        for child in root.children:
            child.update_gamestate()
            all_moves = self.get_all_moves(child.game_state)
            self.calculate_layer(child, all_moves, False)

        print(root.children[0].game_state)
        print(root.children[0].value)
        print(root.children[0].move)

    def calculate_layer(self, root, all_moves: list, our_move: bool):
        for move in all_moves:
            node = Node(root.game_state, self.evaluate(root.game_state, move), [], move)
            if not our_move:
                node.value *= -1
            root.add_child(node)

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

    def evaluate(self, game_state: GameState, move: Move):
        """
        Evaluates a single move and returns a score
        :param game_state: a game state
        :param move: a move
        :return: score
        """
        scores = 0
        col = self.check_column(game_state, move)
        if col == CHECKS["INVALID"]:
            return -1
        else:
            if col == CHECKS["SCORING"]:
                scores += 1
            row = self.check_row(game_state, move)
            if row == CHECKS["INVALID"]:
                return -1
            else:
                if row == CHECKS["SCORING"]:
                    scores += 1
                square = self.check_square(game_state, move)
                if square == CHECKS["INVALID"]:
                    return -1
                else:
                    if square == CHECKS["SCORING"]:
                        scores += 1
        return SCORES[scores]

    def check_row(self, game_state: GameState, move: Move):
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
            self.debug("row invalid")
            return CHECKS["INVALID"]
        elif valid:
            return CHECKS["VALID"]
        return CHECKS["SCORING"]

    def check_column(self, game_state: GameState, move: Move):
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
            self.debug("column invalid")
            return CHECKS["INVALID"]
        elif valid:
            return CHECKS["VALID"]
        return CHECKS["SCORING"]

    def check_square(self, game_state: GameState, move: Move):
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
        row = move.i // m
        column = move.j // n
        valid = False
        # iterate over each row
        for i in range(m):
            # then each column
            for j in range(n):
                curr = game_state.board.get(m * row + i, n * column + j)
                # Do we have an empty cell?
                if curr == 0:
                    # Is this empty cell the move we currently want to make?
                    if m * row + i == move.i and n * column + j == move.j:
                        pass
                    else:
                        valid = True
                else:
                    values.append(curr)
        if move.value in values:
            self.debug("square invalid")
            return CHECKS["INVALID"]
        elif valid:
            return CHECKS["VALID"]
        return CHECKS["SCORING"]

    def debug(self, text):
        if DEBUG:
            print("-" * 25)
            print(text)
            print("-" * 25)

    def minimax(self, node: Node, depth: int, alpha: int, beta: int, is_maximising_player: bool) -> Node:
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
            return evaluate(node)

        children = node.children

        if is_maximising_player:
            maxValue = Node(None, -math.inf, None)
            for child in children:
                value = minimax(child, depth-1, alpha, beta, False)
                maxValue = max([maxValue, value], key=lambda state: state.value)
                beta = max(maxValue.value, beta)
                if beta <= alpha:
                    break
            return maxValue
        else:
            minValue = Node(None, math.inf, None)
            for child in children:
                value = minimax(child, depth-1, alpha, beta, True)
                minValue = max([minValue, value], key=lambda state: state.value)
                beta = min(minValue, beta)
                if beta <= alpha:
                    break
            return minValue


class Node:
    def __init__(self, game_state, value, move):
        self.game_state = game_state
        self.value = value
        self.children = []
        self.move = move

    def __str__(self):
        for child in self.children:
            if child.value == -1:
                pass
            print(str(child.move) + " has value: " + str(child.value))

    def add_child(self, node):
        if (node.value == -1):
            return
        self.children.append(node)

    def update_gamestate(self):
        self.game_state.board.put(self.move.i, self.move.j, self.move.value)

    def has_children(self):
        return bool(self.children)
