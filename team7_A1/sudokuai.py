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
DEBUG = True

class SudokuAI(competitive_sudoku.sudokuai.SudokuAI):
    """
    Sudoku AI that computes a move for a given sudoku configuration.
    """

    """
    TODO:
        - function to generate all legal moves
            - pruning?
        - evaluation function
        - minimax tree search algorithm to find best move
    """

    def __init__(self):
        self.highest_value = -1
        super().__init__()

    def compute_best_move(self, game_state: GameState) -> None:
        N = game_state.board.N

        all_moves = self.get_all_moves(game_state)

        for move in all_moves:
            eval = self.eval(game_state, move)
            if eval == -1:
                self.debug(str(eval))
                self.debug(str(move))
                pass
            else:
                if eval > self.highest_value:
                    self.highest_value = eval
                    self.propose_move(move)
                self.debug(str(eval))
                self.debug(str(move))
            # if eval(move) > self.best_move[2]: self.best_move = move else continue


    def get_all_moves(self, game_state: GameState):
        N = game_state.board.N

        def possible(i, j, value):
            return game_state.board.get(i, j) == SudokuBoard.empty and not TabooMove(i, j, value) in game_state.taboo_moves

        return [Move(i, j, value) for i in range(N) for j in range(N) for value in range(1, N+1) if possible(i, j, value)]

    def eval(self, game_state: GameState, move: Move):
        """
            Evaluates a single move
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
        index = move.i
        values = []
        valid = False
        for i in range(game_state.board.N):
            if i == move.j:
                pass
            elif (game_state.board.get(index, i) != 0):
                values.append(game_state.board.get(index, i))
            else:
                valid =  True
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
        index = move.j
        values = []
        valid = False
        for k in range(game_state.board.N):
            if k == move.i:
                pass
            elif (game_state.board.get(index, k) != 0):
                values.append(game_state.board.get(index, k))
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
                curr = game_state.board.get(m*row + i, n*column + j)
                # Do we have an empty cell?
                if curr == 0:
                    # Is this empty cell the move we currently want to make?
                    if m*row + i == move.i and n*column + j == move.j:
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

    def get_children(self, state: Node) -> List[Node]:
        """
        Returns a list of states that follow form state
        :param state:
        :return: list of GameState
        """
        pass
        # return Node.get_children

    def minimax(self, state: Node, depth: int, alpha: float, beta: float, isMaximisingPlayer: bool) -> tuple:
        """
        Recursively evaluates nodes in game tree
        :param state: starting state
        :param depth: terminal search depth
        :param alpha: pruning
        :param beta: pruning
        :param isMaximisingPlayer: isMaximisingplayer
        :return: tuple (x,y,val) where val is in {1...N}
        """
        pass
        # if depth == 0 or not state.has_children:
        #     return evaluate(state)
        #
        # children = getChildren(state);
        # if ismaximisingPlayer:
        #     maxValue = -math.inf
        #     for child in children:
        #         value = minimax(child, depth-1, alpha, beta, False)
        #         maxValue = get_minmax([maxValue, value], True)
        #         beta = get_minmax([maxValue, beta], True)
        #         if beta[2] <= alpha[2]:
        #             break
        #     return maxValue
        # else:
        #     minValue = math.inf
        #     for child in children:
        #         value = minimax(child, depth-1, alpha, beta, True)
        #         minValue = get_minmax([minValue, value], False)
        #         beta = get_minmax([minValue, beta], False)
        #         if beta[2] <= alpha[2]:
        #             break
        #     return minValue

    def get_minmax(self, list_nodes:List, max:bool) -> dict[tuple, float]:
        """
        makes a key value pair of the nodes with only the value
        :param list_nodes:
        :return:
        """
        pass
        # dic = {}
        # for node in list_nodes:
        #     for x, y, val in node:
        #         dic[(x,y,val)]=val
        #
        # if max:
        #     return max(dic, key=dic.get)
        # else:
        #     return min(dic, key=dic.get)
