from auxiliary import coo2ind, box2coo
from competitive_sudoku.sudoku import GameState
from typing import List, Set, Tuple
from itertools import combinations


def naked_pairs_triples(game_state: GameState, little_num: List[Set[int]]) -> List[Set[int]]:
    """
    Prune the little_num by finding naked pairs and triples

    Naked pairs:
    "A Naked Pair (also known as a Conjugate Pair) is a set of two candidate numbers sited in two cells
    that belong to at least one unit in common. That is, they reside in the same row, column or box.
    It is clear that the solution will contain those values in those two cells, and all other candidates with those
    numbers can be removed from whatever unit(s) they have in common."
    [ Andrew Stuart : https://www.sudokuwiki.org/Naked_Candidates ]

    Naked triples:
    "A Naked Triple is slightly more complicated because it does not always imply three numbers each in three cells.

    Any group of three cells in the same unit that contain IN TOTAL three candidates is a Naked Triple.
    Each cell can have two or three numbers, as long as in combination all three cells have only three numbers.
    When this happens, the three candidates can be removed from all other cells in the same unit.

    The combinations of candidates for a Naked Triple will be one of the following:

    (123) (123) (123) - {3/3/3} (in terms of candidates per cell)
    (123) (123) (12) - {3/3/2} (or some combination thereof)
    (123) (12) (23) - {3/2/2/}
    (12) (23) (13) - {2/2/2}"
    [ Andrew Stuart : https://www.sudokuwiki.org/Naked_Candidates ]

    Finding these naked pairs and triples by checking each row (naked_row), col (naked_col), box (naked_box) individually.

    :param game_state: the current game state
    :param little_num: List[Set], size: N^2, contains the candidate values for each cell
    :return: updated little_num
    """

    N = game_state.N
    m = game_state.board.m
    n = game_state.board.n
    little_num = naked_row(little_num, m, n)
    little_num = naked_col(little_num, m, n)
    little_num = naked_box(little_num, m, n)
    return little_num


def naked_box(little_num: List[Set[int]], m: int, n: int) -> List[Set[int]]:
    """
    Checks all legal moves in a box, and if it's the last possiblitiy
    return the moves that are certain

    :return:
    """
    N = n*m
    for box in range(N):
        pairs_list = []
        triples_list = []
        for coo in box2coo(box, n, m):
            if len(little_num[coo2ind(coo[0], coo[1], N)]) == 2:
                pairs_list.append(((coo[0], coo[1]), little_num[coo2ind(coo[0], coo[1], N)]))
            if len(little_num[coo2ind(coo[0], coo[1], N)]) == 2:
                triples_list.append(((coo[0], coo[1]), little_num[coo2ind(coo[0], coo[1], N)]))
        little_num = prune_naked(little_num, check_naked(pairs_list, 2), m, n, 2)
        little_num = prune_naked(little_num, check_naked(pairs_list, 3), m, n, 3)
    return little_num


def naked_row(little_num: List[Set[int]], m: int, n: int)-> List[Set[int]]:
    """

    :return:
    """
    N = n*m
    for row in range(N):
        pairs_list = []
        triples_list = []
        # get coo and sets that are of size 2 and 3
        for col in range(N):
            if len(little_num[coo2ind(row, col, N)]) == 2:
                pairs_list.append(((row, col), little_num[coo2ind(row, col, N)]))
            if len(little_num[coo2ind(row, col, N)]) == 2:
                triples_list.append(((row, col), little_num[coo2ind(row, col, N)]))
        little_num = prune_naked(little_num, check_naked(pairs_list, 2), m, n, 2)
        little_num = prune_naked(little_num, check_naked(pairs_list, 3), m, n, 3)

    return little_num


def naked_col(little_num: List[Set[int]], m: int, n: int) -> List[Set[int]]:
    """

    :return:
    """
    N = n*m
    for col in range(N):
        pairs_list = []
        triples_list = []
        # get coo and sets that are of size 2 and 3
        for row in range(N):
            if len(little_num[coo2ind(row, col, N)]) == 2:
                pairs_list.append(((row, col), little_num[coo2ind(row, col, N)]))
            if len(little_num[coo2ind(row, col, N)]) == 2:
                triples_list.append(((row, col), little_num[coo2ind(row, col, N)]))
        little_num = prune_naked(little_num, check_naked(pairs_list, 2), m, n, 2)
        little_num = prune_naked(little_num, check_naked(pairs_list, 3), m, n, 3)
    return little_num


def check_naked(arr: List[Tuple[Tuple[int, int],Set[int]]], r: int) -> List[Tuple[Tuple[int, int], Set[int]]]:
    """

    :param arr:
    :param r:
    :return:
    """
    combis = combinations(arr, r)
    all_combis = []
    for combi in combis:
        temp_set = combi[0][1].copy()
        for i in range(len(combi[0])):
            temp_set.update(combi[0][i][1])
        if len(temp_set) == r:
            for i in range(len(combi[0])):
                all_combis.append(combi[0])
    return all_combis


def prune_naked(little_num: List[Set[int]], arr: List[Tuple[Tuple[int, int],Set[int]]], m: int, n: int, r: int) ->  List[Set[int]]:
    """

    :param little_num:
    :param arr:
    :return:
    """
    N = m*n
    for cell in arr:
        row = cell[0][0]
        col = cell[0][1]
        val = cell[1]


        for i in range(N):
            # remove combi out of row
            temp_set = little_num[coo2ind(row, i, N)].copy()
            temp_set.update(val)
            if len(temp_set) != r:
                little_num[coo2ind(row, i, N)].difference_update(val)

            # remove combi out of col
            temp_set = little_num[coo2ind(i, col, N)].copy()
            temp_set.update(val)
            if len(temp_set) != r:
                little_num[coo2ind(i, col, N)].difference_update(val)

            # remove combi out of box
            temp_set = little_num[coo2ind(i, col, N)].copy()
            temp_set.update(val)
            if len(temp_set) != r:
                little_num[coo2ind(i, col, N)].difference_update(val)
    return little_num