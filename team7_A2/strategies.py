from competitive_sudoku.sudoku import Move, SudokuBoard, GameState, TabooMove
from typing import List, Set
from team7_A2.evaluate import evaluate
import logging
import numpy as np
log = logging.getLogger("sudokuai")


def is_empty(board: SudokuBoard, m, n):
    log.debug(f"[{m}, {n}] has value {board.get(m,n)}")
    return board.get(m, n) == 0


def get_row(board: SudokuBoard, m):
    return [board.get(m, n) for n in range(board.N) if board.get(m, n) != 0]


def get_column(board: SudokuBoard, n):
    return [board.get(m, n) for m in range(board.N) if board.get(m, n) != 0]


def get_square(board: SudokuBoard, m, n):
    return [1, 2, 3]


def only_choice(game_state: GameState) -> List[Move]:
    """
        Checks for any moves if they complete a region.
        If they do, add them to the possible moves, else
        discard them.
    """
    N = game_state.board.N
    all_moves = []
    for i in range(N):
        for j in range(N):
            if not is_empty(game_state.board, i, j):
                pass
            else:
                moves = []
                for value in range(1, N+1):
                    curr = Move(i, j, value)
                    if evaluate(game_state, curr) == -1:
                        pass
                    else:
                        moves.append(curr)
                if len(moves) == 1:
                    all_moves.append(moves[0])
    log.critical(f"only_choice returned {str(len(all_moves))} moves")
    for move in all_moves:
        log.info(f"{move}")
    return all_moves



def generate_candidates(game_state: GameState) -> tuple(List[Set]):
    """
    Generates all candidate values for all empty cells in the sudoku
    :param game_state:
    :return: List of size N*N containing a set with candidate values for each cell
    """

    N = game_state.board.N
    m = game_state.board.m
    n = game_state.board.n

    def calc_box(x, y):
        i_rsq = x // m
        i_csq = y // n
        return np.ravel_multi_index((i_rsq, i_csq), (n, m))

    # initialize sets for all cells
    all_moves = [set()] * (N*N)
    row_set = [{val for val in range(1, N + 1)}] * N
    col_set = [{val for val in range(1, N + 1)}] * N
    box_set = [{val for val in range(1, N + 1)}] * N

    # empty_cells contains all empty cells
    empty_cells = []
    for i in range(N):
        for j in range(N):
            if game_state.board.get(i, j) != SudokuBoard.empty:
                row_set[i].remove(game_state.board.get(i, j))
                row_set[j].remove(game_state.board.get(i, j))
                sq_set[calc_box(i, j)].remove(game_state.board.get(i, j))
            else:
                empty_cells.append((i, j))

    for empty_cell in empty_cells:
        i_row = empty_cell[0]
        i_col = empty_cell[1]
        i_box = calc_box(i_row, i_col)
        can_vals = row_set[i_row].intersection(col_set[i_col]).intersection(box_set[i_box])
        for can_val in can_vals:
            if not TabooMove(i_row, i_col, can_val) in game_state.taboo_moves:
                #all_moves.append(Move(i_row, i_col, pos_val))
                all_moves[np.ravel_multi_index((i_row, i_col), (N, N))].update(can_val)
    return (all_moves, row_set, col_set, box_set)

def prune_strategy(game_state: GameState, all_moves: List, row_set: List, col_set: List, box_set: List):
    """

    :param game_state:
    :param all_moves:
    :param row_set:
    :param col_set:
    :param box_set:
    :return:
    """

    pass


# class HiddenTwin:
#     def __init__(self, all_moves, board):
#         self.all_moves = all_moves
#         self.board = board
#         self.return_moves = []

#     def prune(self):
#         """
#         We now have all moves and the current board. For every move,
#         we need to check if the possible values have an intersection
#         with possible values in the same row, column and square. If this
#         is the case, then it might be possible that the move with this 
#         intersecting value is a taboo move that should be avoided.

#         TODO: if a value intersect with another move, yet this other move
#         also still has multiple possible values, should we still exclude?
#         """
#         for move in self.all_moves:
#             row_moves = [row_move for row_move in self.all_moves if row_move.j == move.j and not row_move is move]
#             column_moves = [column_move for column_move in self.all_moves if column_move.j == move.j and not column_move is move]
#             square_indices = {
#                 'i': [],
#                 'j': []
#             }
#             m = self.board.m
#             n = self.board.n
#             column = move.i // m
#             row = move.j // n
#             for i in range(m):
#                 for j in range(n):
#                     if m * row + i == move.j and n * column + j == move.i:
#                         pass
#                     else:
#                         square_indices['i'].append(i)
#                         square_indices['j'].append(j)
#             square_moves = [square_move for square_move in self.all_moves if move.j in square_indices['j'] and move.i in square_indices['i']]

#             self.check_row(row_moves, move)
#             self.check_column(column_moves, move)
#             self.check_square(square_moves, move)

#             return self.return_moves


#     def check_row(self, row_moves, move):
#         if len(row_moves) == 0:
#             return
#         single = len(row_moves) == 1
#         print(f"{if single return 'There is only 1 move available'}")
#         values = [[] * self.board.m]
#         # Get the possible values per empty cell
#         for row_move in row_moves:
#             values[row_move.j].append(row_move.value)
#         for cell_values in values:
#             print(cell_values)


#     def check_column(self, column_moves, move):
#         pass

#     def check_square(self, square_moves, move):
#         pass

#     def print_difference(self):
#         print("Pruned moves due to HiddenTwin are: (symmetric)")
#         print(list(set(self.all_moves) - set(self.return_moves)))

#         print("Pruned moves by HiddenTwin are: (asymmetric)")
#         print((set(self.all_moves) ^ set(self.return_moves)))

def last_box():
    """
    Checks all legal moves in a box, and if it's the last possiblitiy
    return the moves that are certain
    :return:
    """
    pass

def last_row():
    """

    :return:
    """
    pass

def last_col():
    """

    :return:
    """
    pass

def hidden_singles():
    last_col()
    last_row()
    last_box()
    pass

def naked_singles():
    """

    :return:
    """
    pass

def naked_pairs():
    """

    :return:
    """
    pass

def naked_triples():
    """
    A Naked Triple is slightly more complicated because it does not always imply three numbers each in three cells.

    Any group of three cells in the same unit that contain IN TOTAL three candidates is a Naked Triple.
    Each cell can have two or three numbers, as long as in combination all three cells have only three numbers.
    When this happens, the three candidates can be removed from all other cells in the same unit.

    (123) (123) (123) - {3/3/3} (in terms of candidates per cell)
    (123) (123) (12) - {3/3/2} (or some combination thereof)
    (123) (12) (23) - {3/2/2/}
    (12) (23) (13) - {2/2/2}
    :return:
    """
    pass