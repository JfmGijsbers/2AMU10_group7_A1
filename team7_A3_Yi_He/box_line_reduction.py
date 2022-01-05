from team7_A3.auxiliary import coo2ind, box2coo
from competitive_sudoku.sudoku import GameState, SudokuBoard
from typing import List, Set, Tuple
from itertools import combinations


def box_line_reduction(game_state: GameState, little_num: List[Set[int]], row_set: List[Set[int]],
                       col_set: List[Set[int]], box_set: List[Set[int]]) -> List[Set[int]]:
    """
    Prune the little_num by using box line reduction

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
    print(little_num)
    N = game_state.board.N
    for i in range(N):
        for j in range(N):
            pass
    return


def check_row(board: SudokuBoard):
    """
    For every row, every square needs to be checked for
    the 
    """
    return
