import numpy as np
from collections import Counter
from typing import List, Tuple, Set


def calc_box(index_row, index_col, m, n):
    """
    Calculates the box index based on the cell coordinates
    :param index_row: cell row index
    :param index_col: cell column index
    :param m: no. rows of a box, no. columns in a sudoku
    :param n: no. col of a box, no. rows in a sudoku
    :return: box index (a value in the range(0,m*n))
    """
    i_rbx = index_row // m
    i_cbx = index_col // n
    return np.ravel_multi_index((i_rbx, i_cbx), (n, m))


def box2coo(i, m, n) -> list:
    """
    Returns a list of all indices of the cells that are in the corresponding box_index box
    :param i: box index
    :param m: no. rows of a box, no. columns in a sudoku
    :param n: no. col of a box, no. rows in a sudoku
    :return: list of all indices of the cells in the respective box
    """
    i_rbx, i_cbx = np.unravel_index(i, (n, m))
    index_row = i_rbx * m
    index_col = i_cbx * n
    coo = []
    for i in range(n):
        for j in range(m):
            coo.append((index_row + i, index_col + j))
    return coo


def ind2coo(index: int, N: int) -> Tuple[int]:
    """
    convert index of a N*N list into a coordinate for a NxN board
    """

    return np.unravel_index(index, (N, N))


def coo2ind(index_row: int, index_col: int, N: int) -> int:
    """
    convert coordinate for a NxN board into index for a N*N list
    """

    return np.ravel_multi_index((index_row, index_col), (N, N))


def get_single_number(arr: List[int]) -> Set[int]:
    """
    returns the values that only occur once in the list
    :param arr: list with integers
    :return: list with only once occuring integers
    """
    # storing the frequencies using Counter
    freq = Counter(arr)
    single_nums = set()
    # traversing the Counter dictionary
    for i in freq:
        # check if any value is 1
        if freq[i] == 1:
            single_nums.add(i)
    return single_nums
