from team7_A2.auxiliary import coo2ind, box2coo
from competitive_sudoku.sudoku import GameState
from typing import List, Set, Tuple
from itertools import combinations


def hidden_pairs_triples(game_state: GameState, little_num) -> List[Set[int]]:
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
    m = game_state.board.m
    n = game_state.board.n

    # prune by row
    little_num = hidden_row(little_num, m, n)
    # prune by col
    little_num = hidden_col(little_num, m, n)
    # prune by box
    little_num = hidden_box(little_num, m, n)
    return little_num


def hidden_row(little_num: List[Set[int]], m: int, n: int) -> List[Set[int]]:
    """

    :param little_num:
    :param m:
    :param n:
    :return:
    """
    N = n*m

    def add_val(dic: dict, val: int, r: int, c: int, val_cell: Set[int]):
        """

        :return:
        """
        if str(val) not in dic:
            dic[str(val)] = [1, [(r, c)]]
        else:
            dic[str(val)] = [dic[str(val)][0] + 1, dic[str(val)][1].append((r, c)), dic[str(val)][2].append(val_cell)]
        return dic

    for row in range(N):
        temp_dic = {}
        pairs_list = []
        triples_list = []
        # assign every possible move to a value
        for col in range(N):
            for val in list(little_num[coo2ind(row, col, N)]):
                temp_dic = add_val(temp_dic, val, row, col, little_num[coo2ind(row, col, N)])
        # return the values that only occur once
        for item in temp_dic.items():
            val = int(item[0])
            count = item[1][0]
            cells = item[1][1]
            cell_val = item[1][2]
            if count == 2:
                pairs_list.append([val, cells, cell_val])
            if count == 2 or count==3:
                triples_list.append([val, cells, cell_val])
        little_num = prune_hidden(little_num, check_hidden(pairs_list, 2), m, n, 2)
        little_num = prune_hidden(little_num, check_hidden(triples_list, 3), m, n, 3)

    return little_num


def hidden_col(little_num: List[Set[int]], m: int, n: int) -> List[Set[int]]:
    """
    checks if it's a valid hidden pair/triples
    """
    N = n*m
    for col in range(N):
        temp_dic = {}
        pairs_list = []
        triples_list = []
        # assign every possible move to a value
        for col in range(N):
            for val in list(little_num[coo2ind(row, col, N)]):
                temp_dic = add_val(temp_dic, val, row, col, little_num[coo2ind(row, col, N)])
        # return the values that only occur once
        for item in temp_dic.items():
            val = int(item[0])
            count = item[1][0]
            cells = item[1][1]
            cell_val = item[1][2]
            if count == 2:
                pairs_list.append([val, cells, cell_val])
            if count == 2 or count==3:
                triples_list.append([val, cells, cell_val])
        little_num = prune_hidden(little_num, check_hidden(pairs_list, 2), m, n, 2)
        little_num = prune_hidden(little_num, check_hidden(triples_list, 3), m, n, 3)
    return little_num


def hidden_box(little_num: List[Set[int]], m: int, n: int) -> List[Set[int]]:
    """
    checks if it's a valid hidden pair/triples
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


def check_hidden(arr: List[List[int, List[Tuple[int, int]], List[Set[int]]]], r: int) -> List[Tuple[Set[Tuple[int, int]], Set[int]]]:
    """
    checks if it's a valid hidden pair/triples
    """

    # arr = [val, [(x,y), (x,y)], [{vals}, {vals}]]
    combis = combinations(arr, r)
    all_combis = []
    for combi in combis:
        val_set = set()
        for i in range(len(combi)):
            val_set.update(combi[i][0])

        all_cells = []
        for i in range(len(combi)):
            for j in range(len(combi[i][1])):
                row = combi[i][1][j][0]
                col = combi[i][1][j][1]
                cell_vals = combi[i][1][j][2]
                all_cells.append(((row, col), cell_vals.intersection(val_set)))

        check_set = set()
        cells_coo = set()
        for i in range(len(all_cells)):
            check_set.update(all_cells[i][1])
            cells_coo.update(all_cells[i][0])
        # cells_coo = list(cells_coo)
        if len(check_set) == r:
            all_combis.append((cells_coo, val_set))
    return all_combis


def prune_hidden(little_num: List[Set[int]], arr: List[Tuple[Tuple[int, int],Set[int]]], m: int, n: int, r: int) ->  List[Set[int]]:
    """

    :param little_num:
    :param arr:
    :param m:
    :param n:
    :param r:
    :return:
    """
    N = m*n
    for cells_val in arr:
        cells = cells_val[0]
        val = cells_val[1]

        for i in range(N):
            if (row, i) not in cells:
                # remove combi out of row
                temp_set = little_num[coo2ind(row, i, N)].copy()
                temp_set.update(val)
                little_num[coo2ind(row, i, N)].difference_update(val)

            if (row, i) not in cells:
                # remove combi out of col
                temp_set = little_num[coo2ind(i, col, N)].copy()
                temp_set.update(val)
                little_num[coo2ind(i, col, N)].difference_update(val)

            if (row, i) not in cells:
                # remove combi out of box
                temp_set = little_num[coo2ind(i, col, N)].copy()
                temp_set.update(val)
                little_num[coo2ind(i, col, N)].difference_update(val)
    return little_num