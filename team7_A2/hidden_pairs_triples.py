from team7_A2.auxiliary import coo2ind, box2coo
from competitive_sudoku.sudoku import GameState
from typing import List, Set, Tuple
from itertools import combinations


def hidden_pairs_triples(game_state: GameState, little_num):
    """
    Prune the little_num by finding hidden pairs and triples

    Hidden pairs:
    Hidden pairs are two cells in at least 1 common unit (row, column, box) that contain both contain two values
    that only occur in those two cells for that respective unit. The pairs are hidden, since there exist other legal
    values for the respective two cells. Those values can be pruned.

    Hidden triples:
    Hidden triples are similar to the pairs, but than with triples. Here under you can read a definition of hidden
    triples by Andrew Stuart:

    "We can extend Hidden Pairs to Hidden Triples. A Triple will consist of three pairs of numbers
    lying in three cells in the same row, column or box, such as [4,8,9], [4,8,9] and [4,8,9]. However, in just the same
    manner as Naked Triples, we don't need exactly three pairs of numbers in three cells for the rules to apply. Only
    that in total there are three numbers remaining in three cells, so [4,8], [4,9] and [8,9] is equally valid. Hidden
    Triples will be disguised by other candidates on those cells, so we have to prise them out by ensuring the Triple
    applies to at least one unit."

    [ Andrew Stuart : https://www.sudokuwiki.org/Hidden_Candidates ]

    Finding these hidden pairs and triples by checking each row (hidden_row), col (hidden_col),
    box (hidden_box) individually.

    :param game_state: the current game state
    :param little_num: List[Set], size: N^2, contains the candidate values for each cell
    :return: updated little_num
    """

    N = game_state.N
    m = game_state.board.m
    n = game_state.board.n
    little_num = hidden_row(little_num, m, n)
    little_num = hidden_col(little_num, m, n)
    little_num = hidden_box(little_num, m, n)
    return little_num


def hidden_row(little_num: List[Set[int]], m: int, n: int)-> List[Set[int]]:
    """

    :return:
    """
    N = n*m
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

    for row in range(N):
        cand_list = []
        # get coo and sets that are of size larger than 4
        for col in range(N):
            if len(little_num[coo2ind(row, col, N)]) > 2:
                cand_list.append(((row, col), little_num[coo2ind(row, col, N)]))
        little_num = prune_hidden(little_num, check_hidden(cand_list, 2), m, n, 2)
        little_num = prune_hidden(little_num, check_hidden(cand_list, 3), m, n, 3)

    return little_num


def hidden_col(little_num: List[Set[int]], m: int, n: int) -> List[Set[int]]:
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
        little_num = prune_hidden(little_num, check_hidden(pairs_list, 2), m, n, 2)
        little_num = prune_hidden(little_num, check_hidden(pairs_list, 3), m, n, 3)
    return little_num


def hidden_box(little_num: List[Set[int]], m: int, n: int) -> List[Set[int]]:
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
        little_num = prune_hidden(little_num, check_hidden(pairs_list, 2), m, n, 2)
        little_num = prune_hidden(little_num, check_hidden(pairs_list, 3), m, n, 3)
    return little_num


def check_hidden(arr: List[Tuple[Tuple[int, int],Set[int]]], r: int) -> List[Tuple[Tuple[int, int], Set[int]]]:
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


def prune_hidden(little_num: List[Set[int]], arr: List[Tuple[Tuple[int, int],Set[int]]], m: int, n: int, r: int) ->  List[Set[int]]:
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