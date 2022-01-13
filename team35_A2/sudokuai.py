#  (C) Copyright Wieger Wesselink 2021. Distributed under the GPL-3.0-or-later
#  Software License, (See accompanying file LICENSE or copy at
#  https://www.gnu.org/licenses/gpl-3.0.txt)

from competitive_sudoku.sudoku import GameState, SudokuBoard, Move
import competitive_sudoku.sudokuai
import copy
from team35_A2.Minimax import MiniMaxAlphaBeta
from team35_A2.Utility import random_move, no_solution_move


class SudokuAI(competitive_sudoku.sudokuai.SudokuAI):
    """
    Sudoku AI that computes a move for a given sudoku configuration.
    """

    def __init__(self):
        super().__init__()

    def compute_best_move(self, game_state: GameState) -> None:
        '''
        Generates the best move for the current turn
        :param game_state: gameState class
        :return: Nothing
        '''

        # Setting parameters
        self.N = game_state.board.N
        self.rows = game_state.board.m
        self.cols = game_state.board.n

        # Even number of made moves -> player 1 in the game
        if len(game_state.moves) % 2 == 0:
            player = 1
        else:
            player = 2

        # Random move until better move is found
        copyState = copy.deepcopy(game_state)
        bestMove = random_move(self.N, self.rows, self.cols, copyState)
        self.propose_move(bestMove)

        solution = False
        movesLeft = copyState.board.squares.count(SudokuBoard.empty)  # Where in the game are we

        # If our agent does not have the last turn -> play move that leads to no solution
        # To skip move
        if movesLeft <= int((self.N * self.N) / 3) and movesLeft % 2 == 0:
            solution, action = no_solution_move(self.N, self.rows, self.cols, copyState)
            if solution:
                self.propose_move(action)

        # If no skip possible, just try to get the best move
        if not solution:
            AI = MiniMaxAlphaBeta(maxDepth=1, player=player, state=copyState)
            eval, move = AI.choose_action()
            self.propose_move(move)
            # Iterative deepening
            for d in range(2, movesLeft + 1):
                AI.maxDepth = d
                eval, move = AI.choose_action()
                self.propose_move(move)
