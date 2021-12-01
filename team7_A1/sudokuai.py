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
        player_1 = True
        root_move = Move(0, 0, 0)
        root = Node(game_state, 0, root_move)

        # First, we need to compute layer 1
        root = self.calculate_children(root, all_moves, player_1)

        # Then, keep computing moves as long as there are
        # moves to make, alternating between
        # friendly moves and hostile moves.
        kids = root.children
        while bool(kids):
            temp_kids = []
            print(str(len(kids)) + " kids looping")
            for child in kids:
                #print(child.board)
                child.update_gamestate()
                new_all_moves = self.get_all_moves(child.game_state)
                print(str(len(new_all_moves)) + " moves possible")
                child = self.calculate_children(child, new_all_moves, player_1)
                for leaf in child.children:
                    temp_kids.append(leaf)
            kids = temp_kids
            print("LAYER FINISHED")
            print(str(len(kids)) + " kids calculated")
            player_1 = not player_1
        for leaf in child.children:
            leaf.update_gamestate()
            leaf.calculate_children()

    def calculate_children(self, root, all_moves: list, our_move: bool):
        for move in all_moves:
            new_game_state = deepcopy(root.game_state)
            new_move = deepcopy(move)
            #node = Node(new_game_state, evaluate(new_game_state, new_move), new_move)
            node = Node(new_game_state, 0, new_move)
            node.calc_value()
            if not our_move:
                node.value *= -1
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

    # def get_children(self, node: Node) -> List[Node]:
    #     """
    #     Returns a list of states that follow form state
    #     :param node: a node with game state
    #     :return: list of GameState
    #     """
    #     return node.children

    # def minimax(self, node: Node, depth: int, alpha: int, beta: int, isMaximisingPlayer: bool) -> tuple:
    #     """
    #     Recursively evaluates nodes in game tree
    #     :param node: starting state
    #     :param depth: terminal search depth
    #     :param alpha: pruning
    #     :param beta: pruning
    #     :param isMaximisingPlayer: isMaximisingplayer
    #     :return: tuple (x,y,val) where val is in {1...N}
    #     """
    #     if depth == 0 or not node.has_children:
    #         return self.evaluate(node)

    #     children = getChildren(node)

    #     if ismaximisingPlayer:
    #         maxValue = Node(None, -math.inf, None)
    #         for child in children:
    #             value = minimax(child, depth-1, alpha, beta, False)
    #             maxValue = max([maxValue, value], key=lambda state: state.value)
    #             beta = max(maxValue.value, beta)
    #             if beta <= alpha:
    #                 break
    #         return maxValue
    #     else:
    #         minValue = Node(None, math.inf, None)
    #         for child in children:
    #             value = minimax(child, depth-1, alpha, beta, True)
    #             minValue = max([minValue, value], key=lambda state: state.value)
    #             beta = min(minValue, beta)
    #             if beta <= alpha:
    #                 break
    #         return minValue


class Node:
    def __init__(self, game_state, value, move):
        self.game_state = game_state
        self.children = []
        self.move = move
        self.value = 0
        self.taboo = False

    def __str__(self):
        for child in self.children:
            if child.value == -1:
                pass
            print(str(child.move) + " has value: " + str(child.value))

    def calc_value(self):
        val = evaluate(self.game_state, self.move)
        if val == -1:
            self.taboo = True
        return val

    def add_child(self, node):
        if (node.value == -1):
            return
        self.children.append(node)

    def update_gamestate(self):
        self.game_state.board.put(self.move.j, self.move.i, self.move.value)
        print(self.game_state.board)


    def has_children(self):
        return bool(self.children)

    def get_children(self):
        return self.children


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
        return CHECKS["INVALID"]
    elif valid:
        return CHECKS["VALID"]
    return CHECKS["SCORING"]