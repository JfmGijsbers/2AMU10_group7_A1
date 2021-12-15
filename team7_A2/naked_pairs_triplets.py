from auxiliary import coo2ind, ind2coo, box2coo, get_single_number
from competitive_sudoku.sudoku import Move, SudokuBoard, GameState, TabooMove


def naked_pairs_triplets(game_state: GameState, little_num):
    N = game_state.N
    m = game_state.board.m
    n = game_state.board.n
    little_num = naked_row(little_num, m, n)
    little_num = naked_col(little_num, m, n)
    little_num = naked_box(little_num, m, n)
    return little_num


def naked_box(little_num, m, n):
    """
    Checks all legal moves in a box, and if it's the last possiblitiy
    return the moves that are certain
    :return:
    """
    N = n*m
    for box in range(N):
        temp_list = []
        for coo in box2coo(box, n, m):
            temp_list.append(list(little_num[coo2ind(coo[0], coo[1])]))
        only_once = get_single_number(temp_list)
        for j in range(N):
            little_num[coo2ind(coo[0], coo[1])].intersection(only_once)
    return little_num


def naked_row(little_num, n, m):
    """

    :return:
    """
    N = n*m
    for row in range(N):
        temp_list = []
        # get coo and sets that are of size 2 and 3
        for col in range(N):
            temp_list.append(list(little_num[coo2ind(row, col)]))
        # check pairs
        # prune pairs
        # check triplets
        # prune triplets
    return little_num


def naked_col(little_num, n, m):
    """

    :return:
    """
    N = n*m
    for col in range(N):
        temp_list = []
        for row in range(N):
            temp_list.append(list(little_num[coo2ind(col, row)]))
        only_once = get_single_number(temp_list)
        for j in range(N):
            little_num[coo2ind(col, row)].intersection(only_once)
    return little_num
