#  (C) Copyright Wieger Wesselink 2021. Distributed under the GPL-3.0-or-later
#  Software License, (See accompanying file LICENSE or copy at
#  https://www.gnu.org/licenses/gpl-3.0.txt)

import random
import time
from competitive_sudoku.sudoku import GameState, Move, SudokuBoard, TabooMove
import competitive_sudoku.sudokuai


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
        super().__init__()

    def compute_best_move(self, game_state: GameState) -> None:
        N = game_state.board.N
        print(N)

        all_moves = self.get_all_moves(game_state)

        for move in all_moves:
            self.eval(game_state, move)

            self.propose_move(move)
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
        score = 0
        if self.check_column(game_state, move):
            score += 1
        if self.check_row(game_state, move):
            score += 1
        if self.check_square(game_state, move):
            score += 1
        return score
        
    def check_row(self, game_state: GameState, move: Move):
        """
            Checks if all cells in a row are filled for a given move.
        """
        index = move.i
        values = []
        for i in range(game_state.board.N):
            if i == move.j:
                pass
            elif (game_state.board.get(index, i) != 0):
                values.append(game_state.board.get(index, i))
            else:
                return False
        if move.value in values:
            return False
        return True

    def check_column(self, game_state: GameState, move: Move):
        """
            Checks if all cells in a column are filled for a given move.
        """
        index = move.j
        values = []
        for i in range(game_state.board.N):
            if i == move.i:
                pass
            elif (game_state.board.get(index, i) != 0):
                values.append(game_state.board.get(index, i))
            else:
                return False
        if move.value in values:
            return False
        return True

    def check_square(self, game_state: GameState, move: Move):
        """
            Checks if all cells in a square are filled for a given move.
        """
        values = []
        for row in range(game_state.board.m):
            for column in range(game_state.board.n):
                print("row: " + str(row) + ", column: " + str(column) + ", move: " + str(move))
                print("x: " + str(row + move.i) + ", y: " + str(column + move.j) + ", move: " + str(move))
                curr = game_state.board.get(row + move.i, column + move.j)
                print(curr)

        return True

    
