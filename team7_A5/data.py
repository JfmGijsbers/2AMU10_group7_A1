from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Callable, ClassVar, Dict, Optional, List, Union, Set
from competitive_sudoku.sudoku import Move, SudokuBoard, GameState, TabooMove
from typing import List, Set, Tuple
import logging
from team7_A3.auxiliary import coo2ind, calc_box, ind2coo


@dataclass
class MoveData:
    """Stores data to be stored and loaded"""
    state: Any
    board: SudokuBoard
    move: Move = Move(0, 0, 0)
    value: int = 0

    def update(self) -> None:
        pass


def generate_candidates(game_state: GameState) -> Tuple[
    List[Move], List[Set[int]], List[Set[int]], List[Set[int]], List[Set[int]]]:
    """
    Obtain all legal moves to get candidate moves,
    list of sets of all placed values for each row, column or box (row_set, col_set, box_set)

    by:
    1. first making the list of sets of all placed values for each row, column or box
        and obtaining all empty cells
    2. determining which values are legal for each cell by taking the intersection of the corresponding
        row, col, box of the respective cell
        and adding it as a Move object to a list of all moves

    :param game_state: the current game state
    :return: Returns a tuple with the following variables:
        :var legal_moves: List[Move], size: variable, contains the possible moves
        :var lil_num: List[Set], size: N^2, contains the candidate values for each cell
        :var row_set: List[Set], size: N, contains the placed numbers of each row
        :var col_set: List[Set], size: N, contains the placed numbers of each col
        :var box_set: List[Set], size: N, contains the placed numbers of each box
    """
    board = game_state.board
    empty_cells, row_set, col_set, box_set = get_sets_empty(board)
    legal_moves, lil_num = get_legal_moves(board.N, board.m, board.n, game_state.taboo_moves, empty_cells, row_set,
                                           col_set, box_set)
    return legal_moves, lil_num, row_set, col_set, box_set


def get_sets_empty(board: SudokuBoard) -> Tuple[List[Tuple[int, int]], List[Set], List[Set], List[Set]]:
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


def get_legal_moves(N: int,
                    m: int,
                    n: int,
                    taboo_moves: List[TabooMove],
                    empty_cells: List[Tuple],
                    row_set: List[Set],
                    col_set: List[Set],
                    box_set: List[Set]) -> Tuple[List[Move], List[Set]]:
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
    lil_num = []
    legal_moves = []
    for i in range(N * N):
        lil_num.append(set())
    for empty_cell in empty_cells:
        i_row = empty_cell[0]
        i_col = empty_cell[1]
        i_box = calc_box(i_row, i_col, m, n)
        can_vals = row_set[i_row].intersection(col_set[i_col]).intersection(box_set[i_box])
        for can_val in can_vals:
            if not TabooMove(i_row, i_col, can_val) in taboo_moves:
                lil_num[coo2ind(i_row, i_col, N)].add(can_val)
                legal_moves.append(Move(i_row, i_col, can_val))
    return legal_moves, lil_num
