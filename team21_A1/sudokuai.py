#  (C) Copyright Wieger Wesselink 2021. Distributed under the GPL-3.0-or-later
#  Software License, (See accompanying file LICENSE or copy at
#  https://www.gnu.org/licenses/gpl-3.0.txt)

from competitive_sudoku.sudoku import GameState
import competitive_sudoku.sudokuai
from team21_A1.helper_functions import get_legal_moves
from team21_A1.tree_search import Tree, find_best_move
from team21_A1.evaluation import evaluate_move


class SudokuAI(competitive_sudoku.sudokuai.SudokuAI):
    """
    Sudoku AI that computes a move for a given sudoku configuration.
    """

    def __init__(self):
        super().__init__()

    def compute_best_move(self, game_state: GameState) -> None:

        # Get all legal moves
        legal_moves = get_legal_moves(game_state)

        what_player_are_we = len(game_state.moves) % 2
        if what_player_are_we == 1:
            initial_scores = game_state.scores[1]-game_state.scores[0]
        else:
            initial_scores = game_state.scores[0]-game_state.scores[1]

        # oh god just submit a move who cares about depth searching
        best_move = legal_moves[0]
        best_score = evaluate_move(game_state, best_move, True, initial_scores)
        self.propose_move(best_move)

        for cur_move in legal_moves[1:]:
            score = evaluate_move(game_state, cur_move, True, initial_scores)
            if score > best_score:
                best_move = cur_move
        self.propose_move(best_move)

        # Now we start doing search tree stuff and offering a new move every depth
        search_tree = Tree(legal_moves, game_state, initial_scores)
        while True:
            # Extend the depth of the trees by 1
            search_tree.add_layer()

            # Return best move in tree for current depth
            best_move = find_best_move(search_tree)
            self.propose_move(best_move)
