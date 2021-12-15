from competitive_sudoku.sudoku import Move, SudokuBoard, GameState, TabooMove
from typing import List, Set
from team7_A2.evaluate import evaluate
import logging
import numpy as np
from auxiliary import coo2ind
from hidden_singles import hidden_singles
from naked_pairs_triplets import naked_pairs_triplets

log = logging.getLogger("sudokuai")

def only_choice():
    pass


def get_strategy(game_state: GameState):
    """
    Determine from the given game state the best fitting strategies
    :param game_state:
    :return:
    """
    return True

def generate_candidates(game_state: GameState):
    """
    Generates all candidate values for all empty cells in the sudoku
    :param game_state:
    :return: List of size N*N containing a set with candidate values for each cell
    """

    N = game_state.board.N
    m = game_state.board.m
    n = game_state.board.n

    def calc_box(x, y):
        i_rsq = x // m
        i_csq = y // n
        return np.ravel_multi_index((i_rsq, i_csq), (n, m))

    # initialize sets for all cells
    all_moves = []
    little_num = [set()] * (N*N)
    row_set = [{val for val in range(1, N + 1)}] * N
    col_set = [{val for val in range(1, N + 1)}] * N
    box_set = [{val for val in range(1, N + 1)}] * N

    # empty_cells contains all empty cells
    empty_cells = []
    for i in range(N):
        for j in range(N):
            if game_state.board.get(i, j) != SudokuBoard.empty:
                row_set[i].remove(game_state.board.get(i, j))
                row_set[j].remove(game_state.board.get(i, j))
                box_set[calc_box(i, j)].remove(game_state.board.get(i, j))
            else:
                empty_cells.append((i, j))

    for empty_cell in empty_cells:
        i_row = empty_cell[0]
        i_col = empty_cell[1]
        i_box = calc_box(i_row, i_col)
        can_vals = row_set[i_row].intersection(col_set[i_col]).intersection(box_set[i_box])
        for can_val in can_vals:
            if not TabooMove(i_row, i_col, can_val) in game_state.taboo_moves:
                #all_moves.append(Move(i_row, i_col, pos_val))
                little_num[coo2ind(i_row, i_col, N)].add(can_val)
                all_moves.append(Move(i_row, i_col, can_val))
    return all_moves, little_num, row_set, col_set, box_set


def get_all_moves(game_state: GameState, strategies: bool) -> list[Move]:
    """
    Get all moves based on the sudoku solving strategies by:
    1. generate_candidates(game_state) - obtain all legal moves (all_moves), all legal values per cell (little_num,
        comparable with the little help numbers of a Sudoku), list of sets of all placed values for each row, column or box
        (row_set, col_set, box_set)
    2. purning functions - prune little_num with respective sudoku solving strategy
    3. update_all_moves(little_num) - convert all candidate values in little_num in Move objects, and thus
        updating all_moves

    definition of the sizes:
        box has n rows, and m cols
        N = n*m
        sudoku has N rows, and N cols
        sudoku has m row boxes, n col boxes

    :var little_num: List[Set], size: N^2, contains the candidate values for each cell
    :var all_moves: List[Move], size: variable, contains the possible moves
    :var row_set: List[Set], size: N, contains the placed numbers of each row
    :var col_set: List[Set], size: N, contains the placed numbers of each col
    :var box_set: List[Set], size: N, contains the placed numbers of each box

    :param game_state: the current game state
    :param strategies: which strategies to use TODO implement strategies check
    :return: a list of Moves objects that are pruned according to the strategies
    """

    # generate all legal moves, all candidate values per cell, and sets of placed numbers for row, col and box
    all_moves, little_num, row_set, col_set, box_set = generate_candidates(game_state)

    # for each strategy prune candidate values per cell (little_num)
    if strategies:
        all_moves, little_num, row_set, col_set, box_set = hidden_singles(game_state, little_num)
        all_moves, little_num, row_set, col_set, box_set = naked_pairs_triplets(all_moves, little_num, row_set, col_set, box_set)
        # all_moves, little_num, row_set, col_set, box_set = hidden_pairs_triplets(all_moves, little_num, row_set, col_set, box_set)
        # all_moves, row_set, col_set, box_set = pointing_pairs(game_state, all_moves, row_set, col_set, box_set)
        # all_moves, row_set, col_set, box_set = box_line_reduc(game_state, all_moves, row_set, col_set, box_set)

    # Update all_moves by converting little_num into a list of Move objects
    all_moves = update_all_moves(little_num)
    return all_moves


def update_all_moves(little_num: List[Set]) -> List[Move]:
    """
    Convert little_num into a list of Move objects
    :param little_num: N^2 size list corresponding to each cell in the sudoku, containing sets for all possible values
    :return: list of possible Move objects
    """
    pass
