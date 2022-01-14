from ..auxiliary import coo2ind, box2coo
from competitive_sudoku.sudoku import GameState, SudokuBoard
from typing import List, Set, Tuple
from itertools import combinations
import math


def pointing_pairs(game_state: GameState, little_num: List[Set[int]], row_set: List[Set[int]],
                   col_set: List[Set[int]], box_set: List[Set[int]]) -> List[Set[int]]:
    """
    Prune the little_num by using pointing pairs

    definition of the sizes:
        box has n rows, and m cols
        N = n*m
        sudoku has N rows, and N cols
        sudoku has m row boxes, n col boxes

    :param game_state: the current game state
    :param little_num: List[Set], size: N^2, contains the candidate values for each cell
    :param row_set: List[Set], size: N, contains the placed numbers of each row
    :param col_set: List[Set], size: N, contains the placed numbers of each col
    :param box_set: List[Set], size: N, contains the placed numbers of each box
    :return: updated little_num
    """
    pass


def check_row(board: SudokuBoard, y, little_num):
    """
    For row y, check if there is a pair/triplet with a value "v" that does not occur
    anywhere else in said square. If such a pair exists, that value can be stripped from
    all other cells in the row.
    """
    square_values = []
    for i in range(board.m):
        if board.get(y, i) == SudokuBoard.empty:
            pass
        else:
            # get the possible values from little_num, and add them to square_values[i]
            square_values[i].append(little_num[i, y])
    for k in range(0, board.N // board.m, board.m):
        values = square_values[k]
        for l in range(1, board.m):
            values = values.intersect(square_values[k + l])
        if len(values) < 2:
            # we got no pairs / triplets
            return
        # elif value in square:
        else:
            # check if the values occur anywhere else in the row, and remove them if they do
            for i in range(board.m):
                if board.get(y, i) == SudokuBoard.empty:
                    pass
                else:
                    for value in values:
                        if value in little_num[i, y]:
                            little_num[i, y].remove(value)
    return little_num


def check_column(board: SudokuBoard, x, little_num):
    """
    For column x, check if there is a pair/triplet with a value "v" that does not occur
    anywhere else in said square. If such a pair exists, that value can be stripped from
    all other cells in the column.
    """
    square_values = []
    for i in range(board.n):
        if board.get(i, y) == SudokuBoard.empty:
            pass
        else:
            # get the possible values from little_num, and add them to square_values[i]
            square_values[i].append(little_num[x, i])
    for k in range(0, board.N // board.n, board.n):
        values = square_values[k]
        for l in range(1, board.n):
            values = values.intersect(square_values[k + l])
        if len(values) < 2:
            # we got no pairs / triplets
            return
        # elif value in square:
        else:
            # check if the values occur anywhere else in the row, and remove them if they do
            for i in range(board.n):
                if board.get(i, y) == SudokuBoard.empty:
                    pass
                else:
                    for value in values:
                        if value in little_num[y, i]:
                            little_num[y, i].remove(value)
    return little_num


def check_square(board: SudokuBoard, x, y, value, little_num) -> bool:
    values = []
    m = board.m
    n = board.n
    column = x // m
    row = y // n
    for i in range(m):
        # then each column
        for j in range(n):
            curr = board.get(n * column + j, m * row + i)
            # Do we have an empty cell?
            if curr == 0:
                # Is this empty cell the move we currently want to make?
                if m * row + i == x and n * column + j == y:
                    pass
                else:
                    values.append(little_num[i, j])
            else:
                values.append(curr)
