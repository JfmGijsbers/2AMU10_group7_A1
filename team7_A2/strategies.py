from competitive_sudoku.sudoku import Move, SudokuBoard, GameState, TabooMove
from typing import List, Set, Tuple
import logging
from team7_A2.auxiliary import coo2ind, calc_box, ind2coo
from team7_A2.hidden_singles import hidden_singles
from team7_A2.naked_pairs_triples import naked_pairs_triples
from team7_A2.hidden_pairs_triples import hidden_pairs_triples
from team7_A2.box_line_reduction import box_line_reduction
from team7_A2.pointing_pairs import pointing_pairs

log = logging.getLogger("sudokuai")


def get_strategy(game_state: GameState):
    """
    Determine from the given game state the best fitting strategies
    :param game_state:
    :return:
    """
    return True


def get_all_moves(game_state: GameState, strategies: bool) -> List[Move]:
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
    :param strategies: which strategies to use TODO implement strategies check
    :return: a list of Moves objects that are pruned according to the strategies
    """

    # generate all legal moves, all candidate values per cell, and sets of placed numbers for row, col and box
    all_moves, little_num, row_set, col_set, box_set = generate_candidates(game_state)

    # for each strategy prune candidate values per cell (little_num)
    if strategies:
        #little_num = hidden_singles(game_state, little_num)
        #little_num = naked_pairs_triples(game_state, little_num)
        #little_num = hidden_pairs_triples(game_state, little_num)
        #little_num = pointing_pairs(game_state, little_num, row_set, col_set, box_set)
        #little_num = box_line_reduction(game_state, little_num, row_set, col_set, box_set)

    # Update all_moves by converting little_num into a list of Move objects
    all_moves = update_all_moves(little_num, game_state.N)
    return all_moves


def generate_candidates(game_state: GameState) -> Tuple[List[Move], List[Set[int]], List[Set[int]], List[Set[int]], List[Set[int]]]:
    """
    Obtain all legal moves (all_moves), all legal values per cell (little_num, comparable with the little
    help numbers of a Sudoku), list of sets of all placed values for each row, column or box (row_set, col_set, box_set)

    by:
    1. first making the list of sets of all placed values for each row, column or box
        and obtaining all empty cells
    2. determining which values are legal for each cell by taking the intersection of the corresponding
        row, col, box of the respective cell
        and adding it as a Move object to a list of all moves
    TODO ik weet niet of we all_moves, row_set, col_set, box_set uberhaupt
        nodig hebben om te returnen, maar beter te veel dan te weinige. Kunnen we altijd nog achteraf eruit halen.

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
    little_num = [set()] * (N*N)
    # initialize sets for all row, col and boxes containing sets with all
    # possible values for each cell, i.e. range(1, N+1)
    row_set = [{val for val in range(1, N + 1)}] * N
    col_set = [{val for val in range(1, N + 1)}] * N
    box_set = [{val for val in range(1, N + 1)}] * N

    # empty_cells contains all empty cells
    empty_cells = []

    # check each cell if it's empty or not
    # if it's empty, add it to the empty cells
    # if it's not empty, remove the value of the cell from the respective row,col,box set
    for i in range(N):
        for j in range(N):
            if game_state.board.get(i, j) != SudokuBoard.empty:
                row_set[i].remove(game_state.board.get(i, j))
                row_set[j].remove(game_state.board.get(i, j))
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


def update_all_moves(little_num: List[Set[int]], N: int) -> List[Move]:
    """
    Convert little_num into a list of Move objects
    :param little_num: N^2 size list corresponding to each cell in the sudoku, containing sets for all possible values
    :return: list of possible Move objects
    """
    all_moves = []
    for i in range(N*N):
        if len(little_num[i]) > 0:
            row, col = ind2coo(i, N)
            for val in little_num[i]:
                all_moves.append(Move(row, col, val))
    return all_moves
