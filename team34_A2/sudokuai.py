#  (C) Copyright Wieger Wesselink 2021. Distributed under the GPL-3.0-or-later
#  Software License, (See accompanying file LICENSE or copy at
#  https://www.gnu.org/licenses/gpl-3.0.txt)

import random
from itertools import chain
from competitive_sudoku.sudoku import GameState, Move, SudokuBoard, TabooMove
import competitive_sudoku.sudokuai

INF = float('inf')


class SudokuAI(competitive_sudoku.sudokuai.SudokuAI):
    """
    Sudoku AI that computes a move for a given sudoku configuration.
    """

    def __init__(self):
        super().__init__()

    # N.B. This is a very naive implementation.
    def compute_best_move(self, game_state: GameState) -> None:
        N = game_state.board.N
        n = game_state.board.n
        m = game_state.board.m

        def minimax(gs: GameState, score, empty_squares, depth, alpha, beta, maximizingPlayer):
            """"
            Implementation of the minimax algorithm. The algorithm creates a search tree evaluating
            all possible moves. Minimax is made more efficient by implementing alpha-beta pruning.

            Parameters:
            ----------
            gs : GameState
                The current game state
            score : int
                The current game score
            empty_squares: list with coordinates of squares (x, y)
                List with all squares that are empty
            depth : int
                The search depth
            alpha : int
                The minimum score of the maximizing player (for alpha-beta pruning)
            beta : int
                The maximum score of the minimizing player (for alpha-beta pruning)
            maximizingPlayer : boolean
                Indicates if it is the maximizing player's turn
            """

            # return when depth reaches 0
            if depth == 0:
                return score, None

            # Make a list of all possible moves
            all_moves = [Move(i, j, value) for (i, j) in empty_squares for value in range(1, N + 1) if
                         possible(gs, i, j, value) and respects_c0(gs, i, j, value)]

            # return if there are no possible moves left
            if len(all_moves) == 0:
                return score, None

            # Initialize best move as None
            bestMove = None

            # Find best move
            # If player is maximizing, find maximum possible evaluation
            if maximizingPlayer:
                # Start with lowest possible value
                maxEval = -INF

                # For all possible moves:
                for move in all_moves:
                    # Calculate how much score the move gives
                    move_score = increase_score(gs, move)

                    # Perform the move (update gamestate, empty_squares and the score)
                    score += move_score
                    empty_squares.remove((move.i, move.j))
                    gs.board.put(move.i, move.j, move.value)

                    # Recursively search the best move for the opposing player
                    eval, _ = minimax(gs, score, empty_squares, depth - 1, alpha, beta, False)

                    # Undo the move (update gamestate, empty_squares and the score)
                    score -= move_score
                    empty_squares.add((move.i, move.j))
                    gs.board.put(move.i, move.j, SudokuBoard.empty)

                    # Check if the move is the new best move
                    if eval > maxEval:
                        maxEval = eval
                        bestMove = move

                    # Update alpha
                    alpha = max(alpha, eval)

                    # Prune if highest score is smaller than lowest score
                    if beta <= alpha:
                        break

                # Return the best move
                return maxEval, bestMove
            else:
                # Start with highest possible value
                minEval = INF

                # For all possible moves:
                for move in all_moves:
                    # Calculate how much score the move gives
                    move_score = increase_score(gs, move)

                    # Perform the move (update gamestate, empty_squares and the score)
                    score -= move_score
                    empty_squares.remove((move.i, move.j))
                    gs.board.put(move.i, move.j, move.value)

                    # Recursively search the best move for the opposing player
                    eval, _ = minimax(gs, score, empty_squares, depth - 1, alpha, beta, True)

                    # Undo the move (update gamestate, empty_squares and the score)
                    score += move_score
                    empty_squares.add((move.i, move.j))
                    gs.board.put(move.i, move.j, SudokuBoard.empty)

                    # Check if the move is the new best move
                    if eval < minEval:
                        minEval = eval
                        bestMove = move

                    # Update beta
                    beta = min(beta, eval)

                    # Prune if highest score is smaller than lowest score
                    if beta <= alpha:
                        break

                # Return the best move
                return minEval, bestMove

        def increase_score(gs: GameState, move: Move):
            """"
            Returns by how much the score increases by Move move.

            Parameters:
            ----------
            gs : GameState
                The current game state
            move : Move
                A possible move
            """
            i, j, value = move.i, move.j, move.value
            regions_solved = 0

            # Values after the move is done:
            row_values = [value] + [gs.board.get(i, j2) for j2 in range(N) if
                                    (gs.board.get(i, j2) != SudokuBoard.empty)]
            column_values = [value] + [gs.board.get(i2, j) for i2 in range(N) if
                                       (gs.board.get(i2, j) != SudokuBoard.empty)]
            subregion_values = [value] + [gs.board.get(i2, j2) for i2 in
                                          range(i - i % m, i - i % m + m) for j2 in
                                          range(j - j % n, j - j % n + n) if
                                          (gs.board.get(i2, j2) != SudokuBoard.empty)]

            if sorted(row_values) in [list(range(1, N + 1))]:
                regions_solved += 1
            if sorted(column_values) in [list(range(1, N + 1))]:
                regions_solved += 1
            if sorted(subregion_values) in [list(range(1, N + 1))]:
                regions_solved += 1

            reward = 0
            if regions_solved == 0:
                return 0
            elif regions_solved == 1:
                reward = 1
            elif regions_solved == 2:
                reward = 3
            elif regions_solved == 3:
                reward = 7

            return reward

        def get_empty_spaces(gs: GameState):
            """"
            Returns the set of all empty spaces.
            """
            return set([(i, j) for i in range(N) for j in range(N) if gs.board.get(i, j) == SudokuBoard.empty])

        def find_nearly_solved_regions(gs: GameState, missing=1):
            """"
            finds all regions missing a max of input parameter. Returns a set of all valid squares.

            Parameters: missing : int
                        The max amount of squares missing from completion. Default is 1.
            """
            empty_squares = get_empty_spaces(gs)
            ns_regions = []
            for square in empty_squares:
                row = [gs.board.get(square[0], j2) for j2 in range(N) if
                       (gs.board.get(square[0], j2) != SudokuBoard.empty)]
                col = [gs.board.get(i2, square[1]) for i2 in range(N) if
                       (game_state.board.get(i2, square[1]) != SudokuBoard.empty)]
                region = [gs.board.get(i2, j2) for i2 in
                          range(square[0] - square[0] % m, square[0] - square[0] % m + m) for j2 in
                          range(square[1] - square[1] % n, square[1] - square[1] % n + n) if
                          (gs.board.get(i2, j2) != SudokuBoard.empty)]
                if len(row) >= N - missing or len(col) >= N - missing or len(region) >= N - missing:
                    ns_regions.append(square)

            return set(ns_regions)

        def find_even_empty_regions(gs: GameState, ):
            uneven_regions = []

            return set(uneven_regions)

        def random_empty_move(gs: GameState):
            while True:
                i = random.randint(0, N - 1)
                j = random.randint(0, N - 1)
                val = random.randint(1, N)
                if (gs.board.get(i, j) == SudokuBoard.empty and possible(gs, i, j, val) and respects_c0(gs, i, j, val)):
                    return Move(i, j, val)

        def possible(gs: GameState, i, j, value):
            """"
            Checks if a Move(i, j, value) is possible. Returns True if the move is possible else
            False.

            Parameters:
            ----------
            gs : GameState
                The current game state
            i : int
                The column of the cell
            j : int
                The row of the cell
            value : int
                The value that is played in the cell
            """
            return gs.board.get(i, j) == SudokuBoard.empty and not TabooMove(i, j, value) in gs.taboo_moves

        def respects_c0(gs: GameState, i, j, value):
            """"
            Checks if a Move(i, j, value) respects c0. Returns True if the move is allowed else
            False.

            Parameters:
            ----------
            gs : GameState
                The current game state
            i : int
                The column of the cell
            j : int
                The row of the cell
            value : int
                The value that is played in the cell
            """
            row_values = [gs.board.get(i, j2) for j2 in range(N) if
                          (j2 != j) and (gs.board.get(i, j2) != SudokuBoard.empty)]
            column_values = [gs.board.get(i2, j) for i2 in range(N) if
                             (i2 != i) and (gs.board.get(i2, j) != SudokuBoard.empty)]
            subregion_values = [game_state.board.get(i2, j2) for i2 in
                                range(i - i % m, i - i % m + m) for j2 in
                                range(j - j % n, j - j % n + n) if
                                (game_state.board.get(i2, j2) != SudokuBoard.empty)]
            value_set = set(chain(row_values, column_values, subregion_values))
            return value not in value_set

        # Initialize the search depth
        depth = 1

        # Initialize empty set for nearly finished regions
        nearly_finished = set()

        # Game loop, keep searching for the best move, while gradually increasing the search depth
        while depth <= len(get_empty_spaces(game_state)):

            if (len(game_state.taboo_moves) == 0 or len(nearly_finished) == 0):
                self.propose_move(random_empty_move(game_state))

            # Create the set of all empty squares of nearly finished regions
            nearly_finished = find_nearly_solved_regions(game_state, 4)

            score, move = minimax(game_state, 0, nearly_finished, depth, -INF, INF, True)
            if move is not None:
                self.propose_move(move)

            # Create set of all uneven regions
            half_finished_regions = find_nearly_solved_regions(game_state, 7)
            half_finished_regions = {square for square in half_finished_regions if square not in nearly_finished}

            score2, move2 = minimax(game_state, 0, half_finished_regions, depth, -INF, INF, True)

            if score2 > score and move2 is not None:
                score = score2
                move = move2
                # print("second tree",move.i, move.j, move.value)
                self.propose_move(move)

            # Create the set of all empty squares not in nearly finished regions
            empty_spots = {square for square in get_empty_spaces(game_state) if
                           square not in set.union(nearly_finished, half_finished_regions)}

            score2, move2 = minimax(game_state, 0, empty_spots, depth, -INF, INF, True)

            if score2 > score and move2 is not None:
                score = score2
                move = move2
                # print("second tree",move.i, move.j, move.value)
                self.propose_move(move)
            if move is not None:
                pass
                # print(f"Best move at depth {depth} is:")
                # print(f"({move.i}, {move.j}, {move.value}), score = {3}")
            depth += 1
