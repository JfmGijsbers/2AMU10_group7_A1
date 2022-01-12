from competitive_sudoku.sudoku import Move, SudokuBoard, GameState, TabooMove
from typing import Any, Callable, ClassVar, Dict, Optional, List, Union, Set, Tuple
import logging
from .node import MoveData
from .auxiliary import coo2ind, calc_box, ind2coo, box2coo
from .strategies.hidden_singles import hidden_singles
from .strategies.naked_pairs_triples import naked_pairs_triples
# from .hidden_pairs_triples import hidden_pairs_triples
from dataclasses import dataclass, field

SCORES = [0, 1, 3, 7]
PRIORITY = [1, 2, 3, 4]


def get_sets_empty(board: SudokuBoard) -> Tuple[List[Tuple[int, int]], List[Set[int]], List[Set[int]], List[Set[int]]]:
    """
    Returns lists of sets of all placed values for each unit, i.e. row, column or box
    and a list with tuple coordinates for each empty cell in board

    :param board: SudokuBoard
    :return: Returns a tuple with the following variables:
        :var empty_cells List[Tuple], size: variable, contains the empty cells
        :var row_set: List[Set], size: N, contains the yet to be placed numbers of each row
        :var col_set: List[Set], size: N, contains the yet to be placed numbers of each col
        :var box_set: List[Set], size: N, contains the yet to be placed numbers of each box
    """

    N = board.N
    m = board.m
    n = board.n

    # initialize sets for all row, col and boxes containing sets with all
    # possible values for each cell, i.e. range(1, N+1)

    # has to be done with for loops or it takes the references
    mk_num_arr = lambda num: set(range(1, N + 1))
    row_set = []
    col_set = []
    box_set = []
    for i in range(N):
        row_set.append(mk_num_arr(N))
        col_set.append(mk_num_arr(N))
        box_set.append(mk_num_arr(N))

    # empty_cells contains all empty cells
    empty_cells = []

    # check each cell if it's empty or not
    # if it's empty, add it to the empty cells
    # if it's not empty, remove the value of the cell from the respective row, col, box set
    for i in range(N):
        for j in range(N):
            if board.get(i, j) != SudokuBoard.empty:
                row_set[i].remove(board.get(i, j))
                col_set[j].remove(board.get(i, j))
                box_set[calc_box(i, j, m, n)].remove(board.get(i, j))
            else:
                empty_cells.append((i, j))
    return empty_cells, row_set, col_set, box_set


def get_legal_moves(board: SudokuBoard,
                    taboo_moves: List[TabooMove],
                    empty_cells: List[Tuple[int, int]],
                    row_set: List[Set[int]],
                    box_set: List[Set[int]],
                    col_set: List[Set[int]]) -> Tuple[Set[Move], List[Set]]:
    """
    # Calculate for every empty cell the possible value by taking the intersection of the respective row,col,box sets
    # This results in all legal values for that respective cell
    # Then, check if the value is not an already played taboo move, if not, add it to legal_moves, cand_moves
    :param N:
    :param m:
    :param n:
    :param taboo_moves:
    :param empty_cells:
    :param row_set:
    :param col_set:
    :param box_set:
    :return: legal_moves, lil_num
    """
    m = board.m
    n = board.n
    N = m * n
    lil_num = []
    legal_moves = set()
    for i in range(N * N):
        lil_num.append(set())
    for empty_cell in empty_cells:
        i_row = empty_cell[0]
        i_col = empty_cell[1]
        i_box = calc_box(i_row, i_col, m, n)
        can_vals = row_set[i_row].intersection(col_set[i_col]).intersection(box_set[i_box])
        for can_val in [*can_vals]:
            if not TabooMove(i_row, i_col, can_val) in taboo_moves:
                lil_num[coo2ind(i_row, i_col, N)].add(can_val)
                legal_moves.add(Move(i_row, i_col, can_val))
    return legal_moves, lil_num


def get_strategy(game_state: GameState):
    """
    Determine from the given game state the best fitting strategies
    :param game_state:
    :return:
    """
    return True


def update_all_moves2(little_num: List[Set[int]], N: int, legal_moves: Set[Move]) -> Tuple[Set[Move],
                                                                                           Set[Move]]:
    """
    Convert little_num into a list of Move objects
    It returns 3 different possible moves list:
        1. list of all moves possible
        2. list of possible taboo moves
        3. list of certain non taboo moves

    :param little_num: N^2 size list corresponding to each cell in the sudoku, containing sets for all possible values
    :return: list of all possible Moves, list of possible taboo Moves, list of certain non-taboo moves
    """
    all_moves = set()
    for i in range(N * N):
        row, col = ind2coo(i, N)
        if len(little_num[i]) >= 1:
            all_moves.add(Move(row, col, val))
    tab_moves = all_moves.difference(legal_moves)
    return all_moves, tab_moves


def update_all_moves(little_num: List[Set[int]], N: int, legal_moves: Set[Move]) -> Tuple[
    Set[Move], Set[Move], Set[Move], Set[Move]]:
    """
    Convert little_num into a list of Move objects
    It returns 3 different possible moves list:
        1. list of all moves possible
        2. list of possible taboo moves
        3. list of certain non taboo moves

    :param little_num: N^2 size list corresponding to each cell in the sudoku, containing sets for all possible values
    :return: list of all possible Moves, list of possible taboo Moves, list of certain non-taboo moves
    """
    all_moves = set()
    ptab_moves = set()
    ntab_moves = set()
    for i in range(N * N):
        row, col = ind2coo(i, N)
        if len(little_num[i]) >= 1:
            for val in little_num[i]:
                all_moves.add(Move(row, col, val))
            if len(little_num[i]) == 1:
                # for val in little_num[i]:
                #     ntab_moves.add(Move(row, col, val))
                ntab_moves.add(Move(row, col, *little_num[i]))
            elif len(little_num[i]) > 1:
                for val in [*little_num[i]]:
                    ptab_moves.add(Move(row, col, val))
    tab_moves = legal_moves.difference(ntab_moves.union(ptab_moves))
    return all_moves, ntab_moves, ptab_moves, tab_moves


def get_all_moves(board: SudokuBoard, taboo_moves: List[TabooMove]) -> Tuple[
    List[Move], List[Move], List[Move], List[Move]]:
    """
    Get all moves based on the sudoku solving strategies by:
    1. generate_legal_moves(game_state) - get all legal moves as candidate moves and a list of sets of all placed
        values for each unit (row_set, col_set, box_set)
    2. purning functions - prune candidate moves with respective sudoku solving strategy
    3. update_all_moves(little_num) - convert all candidate moves into Move objects

    definitions:
        box has n rows, and m cols
        N = n*m
        sudoku has N rows, and N cols
        sudoku has m row boxes, n col boxes

    :var cand_moves: List[Set], size: N^2, contains the candidate values for each cell
    :var all_moves: List[Move], size: variable, contains the possible moves
    :var row_set: List[Set], size: N, contains the placed numbers of each row
    :var col_set: List[Set], size: N, contains the placed numbers of each col
    :var box_set: List[Set], size: N, contains the placed numbers of each box

    :param game_state: the current game state
    :param strategies: which strategies to use
    :return: a list of Moves objects that are pruned according to the strategies
    """
    # Determine which strategies to play
    strategies = get_strategy(board)

    # generate all legal moves, all candidate values per cell, and sets of placed numbers for row, col and box
    empty_cells, row_set, col_set, box_set = get_sets_empty(board)
    legal_moves, lil_num = get_legal_moves(board, taboo_moves, empty_cells, row_set, col_set, box_set)

    # for each strategy prune candidate values per cell (little_num)
    if strategies:
        lil_num = hidden_singles(board.m, board.n, lil_num)
        # little_num = naked_pairs_triples(game_state, little_num)
        # little_num = hidden_pairs_triples(game_state, little_num)
        # little_num = pointing_pairs(game_state, little_num, row_set, col_set, box_set)
        # little_num = box_line_reduction(game_state, little_num, row_set, col_set, box_set)

    # Update all_moves by converting little_num into a list of Move objects
    all_moves, ntab_moves, ptab_moves, tab_moves = update_all_moves(lil_num, board.N, legal_moves)
    return [*all_moves], [*ntab_moves], [*ptab_moves], [*tab_moves]
