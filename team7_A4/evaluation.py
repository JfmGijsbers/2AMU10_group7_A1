from competitive_sudoku.sudoku import Move, SudokuBoard, GameState, TabooMove
from typing import Any, Callable, ClassVar, Dict, Optional, List, Union, Set, Tuple
import logging
from .node import MoveData
from .auxiliary import coo2ind, calc_box, ind2coo, box2coo

log = logging.getLogger("sudokuai")
SCORES = [0, 1, 3, 7]
PRIORITY = [1, 2, 3, 4]


def get_priority(n_empty: int):
    if n_empty == 1:
        return PRIORITY[1]
    elif n_empty == 2:
        return PRIORITY[2]
    else:
        return PRIORITY[3]


def check_row(board: SudokuBoard, move: Move) -> Tuple[int, int]:
    """
    Checks if the move completes the row by
    getting all other values of the row and checking if there is any other empty cell
    :param board: sudoku board
    :param move: proposed move
    :return: 1 if move completes the row, 0 otherwise
    """
    row_val = [board.get(move.i, k) for k in range(board.N) if k != move.j]
    if 0 in row_val:
        n_empty = row_val.count(0)
        return 0, get_priority(n_empty)
    else:
        return 1, PRIORITY[0]


def check_column(board: SudokuBoard, move: Move) -> Tuple[int, int]:
    """
    Checks if the move completes the col by
    getting all other values of the col and checking if there is any other empty cell
    :param board: sudoku board
    :param move: proposed move
    :return: 1 if move completes the col, 0 otherwise
    """
    col_val = [board.get(k, move.j) for k in range(board.N) if k != move.i]
    if 0 in col_val:
        n_empty = col_val.count(0)
        return 0, get_priority(n_empty)
    else:
        return 1, PRIORITY[0]


def check_box(board: SudokuBoard, move: Move) -> Tuple[int, int]:
    """
    Checks if the move completes the box by
    getting all other values of the box and checking if there is any other empty cell
    :param board: sudoku board
    :param move: proposed move
    :return: 1 if move completes the box, 0 otherwise
    """
    m = board.m
    n = board.n
    i_box = calc_box(move.i, move.j, m, n)
    box_cells = box2coo(i_box, m, n)
    box_val = [board.get(cell[0], cell[1]) for cell in box_cells if not (cell[0] == move.i and cell[1] == move.j)]
    if 0 in box_val:
        n_empty = box_val.count(0)
        return 0, get_priority(n_empty)
    else:
        return 1, PRIORITY[0]


def evaluate_val(board: SudokuBoard, move: Move) -> Tuple[int, int]:
    """
    Evaluates a single move and returns a score
    Score depends on how many units the move completes,
    where units are either a row, col or box
    non-legal moves moves return -1
    :param board: a game state
    :param move: a move
    :return: score
    """
    col, col_p = check_column(board, move)
    row, row_p = check_row(board, move)
    box, box_p = check_box(board, move)
    n_units = col + row + box
    return SCORES[n_units], min(col_p, row_p, box_p)


def evaluate(move: Move, board: SudokuBoard):
    value, priority = evaluate_val(board, move)
    move_data = MoveData(move, value, priority, board)
    return move_data
