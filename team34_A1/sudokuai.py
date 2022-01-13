#  (C) Copyright Wieger Wesselink 2021. Distributed under the GPL-3.0-or-later
#  Software License, (See accompanying file LICENSE or copy at
#  https://www.gnu.org/licenses/gpl-3.0.txt)

import random
import time
from competitive_sudoku.sudoku import GameState, Move, SudokuBoard, TabooMove
import competitive_sudoku.sudokuai
from competitive_sudoku.execute import solve_sudoku


class SudokuAI(competitive_sudoku.sudokuai.SudokuAI):
    """
    Sudoku AI that computes a move for a given sudoku configuration.
    """

    def __init__(self):
        super().__init__()

    def compute_best_move(self, game_state: GameState) -> None:
        N = game_state.board.N
        n = game_state.board.n
        m = game_state.board.m

        def respects_c0(i, j, value):
            row_values = [game_state.board.get(i, j2) for j2 in range(N) if
                          (j2 != j) and (game_state.board.get(i, j2) != SudokuBoard.empty)]
            column_values = [game_state.board.get(i2, j) for i2 in range(N) if
                             (i2 != i) and (game_state.board.get(i2, j) != SudokuBoard.empty)]
            subregion_values = subregion_values = [game_state.board.get(i2, j2) for i2 in
                                                   range(i - i % n, i - i % n + n) for j2 in
                                                   range(j - j % m, j - j % m + m) if ((j2 != j) and (i2 != i)) and (
                                                               game_state.board.get(i2, j2) != SudokuBoard.empty)]

            return value not in row_values + column_values + subregion_values

        def evaluate_state(game_state, additional_move=None):
            """
            Current implementation: Difference between player 2 and player 1 score
            Assumes that it is the turn of player 1
            """
            if additional_move is None:
                return game_state.scores[0] - game_state.scores[1]
            if additional_move is not None:
                i, j, value = additional_move
                regions_solved = 0

                # Values after the move is done:
                row_values = [value] + [game_state.board.get(i, j2) for j2 in range(N) if
                                        (game_state.board.get(i, j2) != SudokuBoard.empty)]
                column_values = [value] + [game_state.board.get(i2, j) for i2 in range(N) if
                                           (game_state.board.get(i2, i) != SudokuBoard.empty)]
                subregion_values = [value] + [game_state.board.get(i2, j2) for i2 in range(i - i % n, i - i % n + n) for
                                              j2 in range(j - j % m, j - j % m + m) if
                                              (game_state.board.get(i2, j2) != SudokuBoard.empty)]

                if sorted(row_values) in [list(range(1, N + 1))]:
                    regions_solved += 1
                if sorted(column_values) in [list(range(1, N + 1))]:
                    regions_solved += 1
                if sorted(subregion_values) in [list(range(1, N + 1))]:
                    regions_solved += 1

                if regions_solved == 0:
                    return game_state.scores[0] - game_state.scores[1]
                elif regions_solved == 1:
                    return game_state.scores[0] - game_state.scores[1] + 1
                elif regions_solved == 2:
                    return game_state.scores[0] - game_state.scores[1] + 3
                elif regions_solved == 3:
                    return game_state.scores[0] - game_state.scores[1] + 7

        def possible(i, j, value):
            return game_state.board.get(i, j) == SudokuBoard.empty and not TabooMove(i, j,
                                                                                     value) in game_state.taboo_moves

        # Propose an initial move, in case of little to no time.
        self.propose_move(Move(1, 1, 1))

        # Select a random non-taboo and respecting c0 move
        # all_moves = [Move(i, j, value) for i in range(N) for j in range(N) for value in range(1, N+1) if possible(i, j, value) and respects_c0(i, j, value)]
        # self.propose_move(random.choice(all_moves))

        # Select a best scoring move, based on increased value
        possible_moves = [(i, j, value) for i in range(N) for j in range(N) for value in range(1, N + 1) if
                          possible(i, j, value) and respects_c0(i, j, value)]
        possible_moves_evaluation = [evaluate_state(game_state, move) for move in possible_moves]
        best_move_index = possible_moves_evaluation.index(max(possible_moves_evaluation))
        best_i, best_j, best_value = possible_moves[best_move_index]
        self.propose_move(Move(best_i, best_j, best_value))
