from auxiliary import coo2ind, ind2coo, box2coo, get_single_number
from competitive_sudoku.sudoku import Move, SudokuBoard, GameState, TabooMove


def hidden_singles(game_state: GameState, little_num):
    """

    :param game_state: Game State
    :param all_moves:
    :param row_set:
    :param col_set:
    :param box_set:
    :return:
    """
    N = game_state.N
    m = game_state.board.m
    n = game_state.board.n
    little_num = last_row(little_num, m, n)
    little_num = last_col(little_num, m, n)
    little_num = last_box(little_num, m, n)
    return little_num


def last_box(little_num, m, n):
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


def last_row(little_num, n, m):
    """

    :return:
    """
    N = n*m
    for row in range(N):
        temp_list = []
        for col in range(N):
            temp_list.append(list(little_num[coo2ind(row, col)]))
        only_once = get_single_number(temp_list)
        for j in range(N):
            little_num[coo2ind(row, col)].intersection(only_once)
    return little_num


def last_col(little_num, n, m):
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
