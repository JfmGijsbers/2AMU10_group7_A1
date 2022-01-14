#  (C) Copyright Wieger Wesselink 2021. Distributed under the GPL-3.0-or-later
#  Software License, (See accompanying file LICENSE or copy at
#  https://www.gnu.org/licenses/gpl-3.0.txt)
import random
import math
from typing import Union, Tuple
from competitive_sudoku.sudoku import GameState, Move, SudokuBoard, TabooMove
import competitive_sudoku.sudokuai
from .evaluate import evaluate

class SudokuAI(competitive_sudoku.sudokuai.SudokuAI):
    """
    Sudoku AI that computes a move for a given sudoku configuration.
    """
    def __init__(self):
        super().__init__()
        self.taboo_moves = []
        self.best_score = -1

    def compute_best_move(self, game_state: GameState) -> None:
        """
        Computes the best move
        :param game_state: the game_state
        :return:
        """
        N = game_state.board.N

        # In order to make the agent more random, loop over a 
        # random range instead of the regular range
        for i in self.rand_range(N):
            for j in self.rand_range(N):
                if game_state.board.get(i, j) != SudokuBoard.empty:
                    continue
                for val in range(1, N+1):
                    move = Move(i, j, val)
                    if TabooMove(i, j, val) in game_state.taboo_moves:
                        continue
                    score = evaluate(game_state, move)
                    if score > self.best_score:
                        self.propose_move(move)
        
    def rand_range(self, n):
        return random.sample(range(0,n), n)