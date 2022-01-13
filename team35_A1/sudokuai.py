#  (C) Copyright Wieger Wesselink 2021. Distributed under the GPL-3.0-or-later
#  Software License, (See accompanying file LICENSE or copy at
#  https://www.gnu.org/licenses/gpl-3.0.txt)

import random
from competitive_sudoku.sudoku import GameState, Move, SudokuBoard, TabooMove
import competitive_sudoku.sudokuai
import copy
from team35_A1.minimax import MiniMaxAlphaBeta
from team35_A1.Evaluation import possible


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

        def split(lst, length):
            '''
            Transformes the list of value of the board to a tuple containing the
            rows of values
            :param lst: list containing all the value of the board
            :param length: the number of rows
            :return: A tuple representing the values of the rows on the board

            Example
            split([1,2,3,4],2)
            >> ([1,2],[3,4])
            '''
            k, m = divmod(len(lst), length)
            return (lst[i * k + min(i, m):(i + 1) * k + min(i + 1, m)]
                    for i in range(length))

        # Setting parameters
        self.N = game_state.board.N
        self.rows = game_state.board.m
        self.cols = game_state.board.n

        # Even number of made moves -> player 1 in the game
        if len(game_state.moves) % 2 == 0:
            player = 1
        else:
            player = 2

        # Generate all the moves
        copyState = copy.deepcopy(game_state)
        all_moves = [Move(i, j, value) for i in range(self.N) for j in range(self.N) for value in
                     range(1, self.N + 1) if possible(i, j, value, copyState, self.rows, self.cols, self.N)]

        # Random move until better move is found
        bestMove = random.choice(all_moves)
        self.propose_move(bestMove)

        movesLeft = copyState.board.squares.count(SudokuBoard.empty)

        # Iterative deepening
        for d in range(1, movesLeft + 1):
            print('        depth', d)
            AI = MiniMaxAlphaBeta(maxDepth=d, player=player)
            eval, move = AI.choose_action(copyState)
            self.propose_move(move)
        print('----------------------')
        print('done')
