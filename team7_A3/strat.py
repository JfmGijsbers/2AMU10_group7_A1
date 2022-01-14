from competitive_sudoku.sudoku import Move, SudokuBoard, GameState, TabooMove
from typing import List, Set, Tuple
import logging
from .auxiliary import coo2ind, calc_box, ind2coo
from .strategies.hidden_singles import hidden_singles
from .timer import Timer

logger = logging.getLogger("sudokuai")
logger.setLevel(logging.CRITICAL)


def get_strategy(game_state: GameState):
    """
    PLACE HOLDER FOR GET STRATEGY
    ==============================
    Determine from the given game state the best fitting strategies
    :param game_state:
    :return:
    """
    return True


@Timer(name="get_all_moves", text="get_all_moves - elapsed time - {:0.4f} seconds", logger=None)
def get_all_moves(game_state: GameState, strategies: bool = True) -> Tuple[List[Move], List[Move]]:
    """
    Get all moves based on the sudoku solving strategies by:
    1. generate_candidates(game_state) - obtain all legal moves (all_moves), all legal values per cell (little_num,
        comparable with the little help numbers of a Sudoku), list of sets of all placed values for each row, column or box
        (row_set, col_set, box_set)
    2. purning functions - prune little_num with respective sudoku solving strategy
    3. update_all_moves(little_num) - convert all candidate values in little_num in Move objects, and thus
        updating all_moves

    definition of the sizes:
        box has n rows, and m cols
        N = n*m
        sudoku has N rows, and N cols
        sudoku has m row boxes, n col boxes

    :var little_num: List[Set], size: N^2, contains the candidate values for each cell
    :var all_moves: List[Move], size: variable, contains the possible moves
    :var row_set: List[Set], size: N, contains the placed numbers of each row
    :var col_set: List[Set], size: N, contains the placed numbers of each col
    :var box_set: List[Set], size: N, contains the placed numbers of each box

    :param game_state: the current game state
    :param strategies: which strategies to use
    :return: a list of Moves objects that are pruned according to the strategies
    """

    # generate all legal moves, all candidate values per cell, and sets of placed numbers for row, col and box
    all_moves, little_num, row_set, col_set, box_set = generate_candidates(game_state)

    # for each strategy prune candidate values per cell (little_num)
    if strategies:
        little_num = hidden_singles(game_state, little_num)
        # HERE OTHER STRATEGIES CAN BE USED FOR EXAMPLE:
        # little_num = naked_pairs_triples(game_state, little_num)
        # little_num = hidden_pairs_triples(game_state, little_num)
        # little_num = pointing_pairs(game_state, little_num, row_set, col_set, box_set)
        # little_num = box_line_reduction(game_state, little_num, row_set, col_set, box_set)

    # Update all_moves by converting little_num into a list of Move objects
    all_moves, pos_taboo, not_taboo, taboo_list = update_all_moves(all_moves, little_num, game_state.board.N)
    return all_moves, taboo_list


@Timer(name="generate_candidates", text="gen_candidates - elapsed time - {:0.4f} seconds", logger=None)
def generate_candidates(game_state: GameState) -> Tuple[
    List[Move], List[Set[int]], List[Set[int]], List[Set[int]], List[Set[int]]]:
    """
    Obtain all legal moves (all_moves), all legal values per cell (little_num, comparable with the little
    help-numbers of a Sudoku), list of sets of all placed values for each row, column or box (row_set, col_set, box_set)

    by:
    1. first making the list of sets of all placed values for each row, column or box
        and obtaining all empty cells
    2. determining which values are legal for each cell by taking the intersection of the corresponding
        row, col, box of the respective cell
        and adding it as a Move object to a list of all moves

    :param game_state: the current game state
    :return: Returns a tuple with the following variables:
        :var little_num: List[Set], size: N^2, contains the candidate values for each cell
        :var all_moves: List[Move], size: variable, contains the possible moves
        :var row_set: List[Set], size: N, contains the placed numbers of each row
        :var col_set: List[Set], size: N, contains the placed numbers of each col
        :var box_set: List[Set], size: N, contains the placed numbers of each box
    """

    N = game_state.board.N
    m = game_state.board.m
    n = game_state.board.n

    # initialize all_moves and little_num
    all_moves = []

    # initialize sets for all row, col and boxes containing sets with all
    # possible values for each cell, i.e. range(1, N+1)

    # has to be done with for loops or it takes the references
    mk_num_arr = lambda num: set(range(1, N + 1))
    row_set = []
    col_set = []
    box_set = []
    little_num = []
    for i in range(N):
        row_set.append(mk_num_arr(N))
        col_set.append(mk_num_arr(N))
        box_set.append(mk_num_arr(N))
    for i in range(N * N):
        little_num.append(set())

    # empty_cells contains all empty cells
    empty_cells = []

    # check each cell if it's empty or not
    # if it's empty, add it to the empty cells
    # if it's not empty, remove the value of the cell from the respective row, col, box set
    for i in range(N):
        for j in range(N):
            if game_state.board.get(i, j) != SudokuBoard.empty:
                row_set[i].remove(game_state.board.get(i, j))
                col_set[j].remove(game_state.board.get(i, j))
                box_set[calc_box(i, j, m, n)].remove(game_state.board.get(i, j))
            else:
                empty_cells.append((i, j))

    # Calculate for every empty cell the possible value by taking the intersection of the respective row,col,box sets
    # This results in all legal values for that respective cell
    # Then, check if the value is not an already played taboo move, if not, add it to all_moves and little_num
    for empty_cell in empty_cells:
        i_row = empty_cell[0]
        i_col = empty_cell[1]
        i_box = calc_box(i_row, i_col, m, n)
        can_vals = row_set[i_row].intersection(col_set[i_col]).intersection(box_set[i_box])
        for can_val in can_vals:
            if not TabooMove(i_row, i_col, can_val) in game_state.taboo_moves:
                little_num[coo2ind(i_row, i_col, N)].add(can_val)
                all_moves.append(Move(i_row, i_col, can_val))
    return all_moves, little_num, row_set, col_set, box_set


@Timer(name="update_all_moves", text="update all moves - elapsed time - {:0.4f} seconds", logger=None)
def update_all_moves(legal_moves: List[Move], little_num: List[Set[int]], N: int) -> Tuple[
    List[Move], List[Move], List[Move], List[Move]]:
    """
    Convert little_num into a list of Move objects
    It returns 3 different possible moves list:
        1. list of all moves possible
        2. list of possible taboo moves
        3. list of certain non taboo moves

    :param little_num: N^2 size list corresponding to each cell in the sudoku, containing sets for all possible values
    :return: list of all possible Moves, list of possible taboo Moves, list of certain non-taboo moves
    """
    all_moves = []
    taboo_list = []
    pos_taboo = []
    not_taboo = []
    for i in range(N * N):
        row, col = ind2coo(i, N)
        if len(little_num[i]) >= 1:
            for val in little_num[i]:
                all_moves.append(Move(row, col, val))
            if len(little_num[i]) == 1:
                for val in little_num[i]:
                    not_taboo.append(Move(row, col, val))
            elif len(little_num[i]) > 1:
                for val in little_num[i]:
                    pos_taboo.append(Move(row, col, val))
    taboo_list = [tab_move for tab_move in legal_moves if tab_move not in all_moves]
    return all_moves, pos_taboo, not_taboo, [*taboo_list]
