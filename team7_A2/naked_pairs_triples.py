from team7_A2.auxiliary import coo2ind, box2coo, calc_box
from competitive_sudoku.sudoku import GameState
from typing import List, Set, Tuple, Union
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

    N = game_state.board.N
    m = game_state.board.m
    n = game_state.board.n
    little_num = naked_row(little_num, m, n)
    little_num = naked_col(little_num, m, n)
    little_num = naked_box(little_num, m, n)
    return little_num


def naked_row(little_num: List[Set[int]], m: int, n: int) -> List[Set[int]]:
    """
    Checks if there are naked pairs or triples in a row
    :param little_num: list of all candidate values
    :param m: number of col boxes, number of cols box
    :param n: number of col boxes, number of rows box
    :return: pruned version of little_num
    """
    N = n*m

    for row in range(N):
        pairs_list = []
        triples_list = []
        # get coordinates of cells with 2 or 3 candidate values
        # cells with 2 values are added to the potential nake pairs pairs_list
        # cells with 2 or 3 values are added to the potential naked triples triples_list
        for col in range(N):
            if len(little_num[coo2ind(row, col, N)]) == 2:
                pairs_list.append(((row, col), little_num[coo2ind(row, col, N)]))
            if len(little_num[coo2ind(row, col, N)]) == 2 or len(little_num[coo2ind(row, col, N)]) == 3:
                triples_list.append(((row, col), little_num[coo2ind(row, col, N)]))
        little_num = prune_naked(little_num, check_naked(pairs_list, 2), m, n, 2, "row")
        little_num = prune_naked(little_num, check_naked(triples_list, 3), m, n, 3, "row")
    return little_num


def naked_col(little_num: List[Set[int]], m: int, n: int) -> List[Set[int]]:
    """
    Checks if there are naked pairs or triples in a col
    :param little_num: list of all candidate values
    :param m: number of col boxes, number of cols box
    :param n: number of col boxes, number of rows box
    :return: pruned version of little_num
    """
    N = n*m
    for col in range(N):
        pairs_list = []
        triples_list = []
        # get coo and sets that are of size 2 and 3
        for row in range(N):
            if len(little_num[coo2ind(row, col, N)]) == 2:
                pairs_list.append(((row, col), little_num[coo2ind(row, col, N)]))
            if len(little_num[coo2ind(row, col, N)]) == 2 or len(little_num[coo2ind(row, col, N)]) == 3:
                triples_list.append(((row, col), little_num[coo2ind(row, col, N)]))
        little_num = prune_naked(little_num, check_naked(pairs_list, 2), m, n, 2, "col")
        little_num = prune_naked(little_num, check_naked(triples_list, 3), m, n, 3, "col")
    return little_num


def naked_box(little_num: List[Set[int]], m: int, n: int) -> List[Set[int]]:
    """
    Checks if there are naked pairs or triples in a box
    :param little_num: list of all candidate values
    :param m: number of col boxes, number of cols box
    :param n: number of col boxes, number of rows box
    :return: pruned version of little_num
    """
    N = n*m
    for box in range(N):
        pairs_list = []
        triples_list = []
        for coo in box2coo(box, n, m):
            if len(little_num[coo2ind(coo[0], coo[1], N)]) == 2:
                pairs_list.append(((coo[0], coo[1]), little_num[coo2ind(coo[0], coo[1], N)]))
            if len(little_num[coo2ind(coo[0], coo[1], N)]) == 2 or len(little_num[coo2ind(coo[0], coo[1], N)]) == 3:
                triples_list.append(((coo[0], coo[1]), little_num[coo2ind(coo[0], coo[1], N)]))
        little_num = prune_naked(little_num, check_naked(pairs_list, 2), m, n, 2, "box")
        little_num = prune_naked(little_num, check_naked(triples_list, 3), m, n, 3, "box")

    return little_num


def check_naked(arr: List[Tuple[Tuple[int, int], Set[int]]], r: int) -> List[List[Union[List, Set]]]:
    """

    :param arr: [((x, y),{val1, val2, (val3)}]
    :param r:
    :return:
    """
    combis = combinations(arr, r)
    all_combis = []
    for combi in combis:
        val_set = set()
        for i in range(len(combi)):
            val_set.union(combi[i][1])
        if len(val_set) == r:
            cells = []
            for i in range(len(combi)):
                cells.append(combi[i][0])
                print(type(combi[i][0]))
            all_combis.append([cells, val_set])
    return all_combis


def prune_naked(little_num: List[Set[int]], arr:  List[List[Union[List, Set]]], m: int, n: int, r: int,
                unit: str) -> List[Set[int]]:
    """

    :param little_num:
    :param arr:
    :param m:
    :param n:
    :param r:
    :param unit:
    :return:
    """
    N = m*n
    for cell in arr:
        cells_set = set(cell[0])
        val_set = cell[1]
        row = cell[0][0][0]
        col = cell[0][0][1]
        box = calc_box(cell[0][0][0], cell[0][0][1], m, n)

        if unit == "row" or unit == "col":
            for i in range(N):
                if unit == "row":
                    # remove combi out of row
                    if (i, row) not in cells_set:
                        little_num[coo2ind(row, i, N)].difference_update(val_set)
                if unit == "col":
                    # remove combi out of col
                    if (col, i) not in cells_set:
                        little_num[coo2ind(i, col, N)].difference_update(val_set)
        if unit == "box":
            for coo in box2coo(box, n, m):
                # remove combi out of box
                if coo not in cells_set:
                    little_num[coo2ind(coo[0], coo[1], N)].difference_update(val_set)
    return little_num