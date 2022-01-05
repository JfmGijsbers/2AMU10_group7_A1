from competitive_sudoku.sudoku import Move, SudokuBoard, GameState
from team7_A3.auxiliary import box2coo, calc_box

SCORES = [0, 1, 3, 7]


def check_row(board: SudokuBoard, move: Move) -> int:
    """
    Checks if the move completes the row by
    getting all other values of the row and checking if there is any other empty cell
    :param board: sudoku board
    :param move: proposed move
    :return: 1 if move completes the row, 0 otherwise
    """
    row_val = [board.get(move.i, k) for k in range(board.N) if k != move.j]
    return 0 if 0 in row_val else 1


def check_column(board: SudokuBoard, move: Move) -> int:
    """
    Checks if the move completes the col by
    getting all other values of the col and checking if there is any other empty cell
    :param board: sudoku board
    :param move: proposed move
    :return: 1 if move completes the col, 0 otherwise
    """
    col_val = [board.get(k, move.j) for k in range(board.N) if k != move.i]
    return 0 if 0 in col_val else 1


def check_box(board: SudokuBoard, move: Move) -> int:
    """
    Checks if the move completes the box by
    getting all other values of the box and checking if there is any other empty cell
    :param board: sudoku board
    :param move: proposed move
    :return: 1 if move completes the box, 0 otherwise
    """
    m = board.m
    n = board.n
    i_box = calc_box(move.i, move.j, m, n)
    box_cells = box2coo(i_box, m, n)
    box_val = [board.get(cell[0], cell[1]) for cell in box_cells if not (cell[0] == move.i and cell[1] == move.j)]
    return 0 if 0 in box_val else 1


def evaluate(parent_game_state: GameState, move: Move) -> int:
    """
    Evaluates a single move and returns a score
    Score depends on how many units the move completes,
    where units are either a row, col or box
    non-legal moves moves return -1
    :param parent_game_state: a game state
    :param move: a move
    :return: score
    """
    board = parent_game_state.board
    col = check_column(board, move)
    row = check_row(board, move)
    box = check_box(board, move)
    n_units = col + row + box
    return SCORES[n_units]
