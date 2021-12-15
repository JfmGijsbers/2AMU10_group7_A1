from auxiliary import coo2ind, ind2coo, box2coo, get_single_number
from competitive_sudoku.sudoku import Move, SudokuBoard, GameState, TabooMove


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


def hidden_box(little_num, m, n):
    """
    Checks all legal moves in a box, and if it's the last possiblitiy
    return the moves that are certain
    :return:
    """
    N = n*m
    for box in range(N):
        temp_list = []
        # get coo and sets that are of size 3 or more
        for coo in box2coo(box, n, m):
            temp_list.append(list(little_num[coo2ind(coo[0], coo[1])]))
        # check pairs
        # prune pairs
        # check triples
        # prune triples
    return little_num


def hidden_row(little_num, n, m):
    """

    :return:
    """
    N = n*m
    for row in range(N):
        temp_list = []
        # get coo and sets that are of size 3 or more
        for col in range(N):
            temp_list.append(list(little_num[coo2ind(row, col)]))
        # check pairs
        # prune pairs
        # check triples
        # prune triples
    return little_num


def hidden_col(little_num, n, m):
    """

    :return:
    """
    N = n*m
    for col in range(N):
        temp_list = []
        # get coo and sets that are of size 3 or more
        for row in range(N):
            temp_list.append(list(little_num[coo2ind(col, row)]))
        # check pairs
        # prune pairs
        # check triples
        # prune triples
    return little_num
