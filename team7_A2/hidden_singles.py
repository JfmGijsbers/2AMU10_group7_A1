from auxiliary import coo2ind, ind2coo, box2coo, get_single_number
from competitive_sudoku.sudoku import Move, SudokuBoard, GameState, TabooMove
from typing import List, Set, Tuple


def hidden_singles(game_state: GameState, little_num: List[Set]) -> List[Set]:
    """
    Prune the little_num by finding hidden singles

    hidden singles:
    Multiple values are legal for a cell, however value X is only possible in this respective cell
    for a certain unit (row, col, box). Therefore, all other values besides X can be pruned.
    This method sometimes also referred as single possibility

    This is done by checking each row (only_row), col (only_col), box (only_box) individually.

    :param game_state: the current game state
    :param little_num: List[Set], size: N^2, contains the candidate values for each cell
    :return: updated little_num
    """
    m = game_state.board.m
    n = game_state.board.n
    # prune by row
    little_num = only_row(little_num, m, n)
    # prune by col
    little_num = only_col(little_num, m, n)
    # prune by box
    little_num = only_box(little_num, m, n)
    return little_num


def only_box(little_num, m, n):
    """
    Checks all legal moves in a box, and if it's the only possiblitiy
    return the moves that are certain
    :param little_num:
    :param m:
    :param n:
    :return:
    """
    N = n*m
    for box in range(N):
        temp_list = []
        # make for every box a
        for coo in box2coo(box, n, m):
            temp_list.append(list(little_num[coo2ind(coo[0], coo[1])]))
        only_once = get_single_number(temp_list)
        for j in range(N):
            if little_num[coo2ind(coo[0], coo[1])].intersection(only_once):
                little_num[coo2ind(coo[0], coo[1])] = little_num[coo2ind(coo[0], coo[1])].intersection(only_once)
    return little_num


def only_row(little_num, n, m):
    """
    Checks all legal moves in a box, and if it's the only possiblitiy
    return the moves that are certain
    :param little_num:
    :param m:
    :param n:
    :return:
    """
    N = n*m

    for row in range(N):
        temp_list = []
        # make for every row a value list
        for col in range(N):
            temp_list.append(list(little_num[coo2ind(row, col)]))
        # return the values that only occur once
        only_once = get_single_number(temp_list)
        # update little_num by taking the intersection if it contains the number that only occurs once
        for j in range(N):
            if little_num[coo2ind(row, col)].intersection(only_once):
                little_num[coo2ind(row, col)] = little_num[coo2ind(row, col)].intersection(only_once)
    return little_num


def only_col(little_num, n, m):
    """
    Checks all legal moves in a box, and if it's the only possiblitiy
    return the moves that are certain
    :param little_num:
    :param m:
    :param n:
    :return:
    """
    N = n*m
    # make for every row a value list
    for col in range(N):
        temp_list = []
        # return the values that only occur once
        for row in range(N):
            temp_list.append(list(little_num[coo2ind(col, row)]))
        only_once = get_single_number(temp_list)
        # update little_num by taking the intersection if it contains the number that only occurs once
        for j in range(N):
            if little_num[coo2ind(row, col)].intersection(only_once):
                little_num[coo2ind(row, col)] = little_num[coo2ind(row, col)].intersection(only_once)
    return little_num