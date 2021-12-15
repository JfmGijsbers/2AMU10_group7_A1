from auxiliary import coo2ind, ind2coo, box2coo, get_single_number
from competitive_sudoku.sudoku import Move, SudokuBoard, GameState, TabooMove


def naked_pairs_triples(game_state: GameState, little_num):
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
        # check triples
        # prune triples
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
