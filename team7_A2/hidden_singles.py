from auxiliary import coo2ind, ind2coo, box2coo, get_single_number
from competitive_sudoku.sudoku import Move, SudokuBoard, GameState, TabooMove
from typing import List, Set, Tuple


def hidden_singles(game_state: GameState, little_num: List[Set[int]]) -> List[Set[int]]:
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
    N = m*n
    # prune by row
    little_num = only_row(little_num, N)
    # prune by col
    little_num = only_col(little_num, N)
    # prune by box
    little_num = only_box(little_num, m, n)
    return little_num


def only_box(little_num: List[Set[int]], m: int, n: int) -> List[Set[int]]:
    """
    Checks all legal values in a box and if a certain value X only occurs in one cell only
    prune all other candidate values of that cell
    :param little_num: list of all candidate values
    :param N: number of rows and columns
    :return: pruned version of little_num
    """
    N = n*m
    for box in range(N):
        coo_box = []
        # Get for every box all corresponding coordinates
        # coo contains coordinates of respective box
        for coo in box2coo(box, n, m):
            coo_box = coo_box + list(little_num[coo2ind(coo[0], coo[1], N)])
            only_once = get_single_number(coo_box)
            if little_num[coo2ind(coo[0], coo[1], N)].intersection(only_once):
                little_num[coo2ind(coo[0], coo[1], N)] = little_num[coo2ind(coo[0], coo[1], N)].intersection(only_once)
    return little_num


def only_row(little_num: List[Set[int]], N: int) -> List[Set[int]]:
    """
    Checks all legal values in a row and if a certain value X only occurs in one cell only
    prune all other candidate values of that cell
    :param little_num: list of all candidate values
    :param N: number of rows and columns
    :return: pruned version of little_num
    TODO als we tijd hebben kunnen we row en col samenvoegen in één functie
    """
    for row in range(N):
        temp_list = []
        # make for every row a value list
        for col in range(N):
            temp_list = temp_list + list(little_num[coo2ind(row, col, N)])
        # return the values that only occur once
        only_once = get_single_number(temp_list)
        # update little_num by taking the intersection if it contains the number that only occurs once
        for col in range(N):
            if little_num[coo2ind(row, col, N)].intersection(only_once):
                little_num[coo2ind(row, col, N)] = little_num[coo2ind(row, col, N)].intersection(only_once)
    return little_num


def only_col(little_num: List[Set[int]], N: int) -> List[Set[int]]:
    """
    Checks all legal values in a column and if a certain value X only occurs in one cell only
    prune all other candidate values of that cell
    :param little_num: list of all candidate values
    :param N: number of rows and columns
    :return: pruned version of little_num
    """
    # make for every col a value list
    for col in range(N):
        temp_list = []
        # return the values that only occur once
        for row in range(N):
            temp_list = temp_list + list(little_num[coo2ind(col, row, N)])
        only_once = get_single_number(temp_list)
        # update little_num by taking the intersection if it contains the number that only occurs once
        for row in range(N):
            if little_num[coo2ind(row, col, N)].intersection(only_once):
                little_num[coo2ind(row, col, N)] = little_num[coo2ind(row, col, N)].intersection(only_once)
    return little_num