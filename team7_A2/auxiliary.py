import numpy as np
from collections import Counter


def calc_box(index_row, index_col, m, n):
    i_rbx = index_row // m
    i_cbx = index_col // n
    return np.ravel_multi_index((i_rbx, i_cbx), (n, m))


def box2coo(i, m, n) -> list:
    i_rbx, i_cbx = np.unravel_index(i, (n, m))
    index_row = i_rbx * m
    index_col = i_cbx * n
    coo = []
    for i in range(n):
        for j in range(m):
            coo.append((index_row + i, index_col + j))
    return coo


def ind2coo(index, N):
    return np.unravel_index(index, (N, N))


def coo2ind(index_row, index_col, N):
    return np.ravel_multi_index((index_row, index_col), (N, N))


def get_single_number(arr):
    # storing the frequencies using Counter
    freq = Counter(arr)
    single_nums = set()
    # traversing the Counter dictionary
    for i in freq:
        # check if any value is 1
        if freq[i] == 1:
            single_nums.add(i)
    return single_nums

