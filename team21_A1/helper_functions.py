from competitive_sudoku.sudoku import GameState, Move, SudokuBoard, TabooMove
import copy


def check_legal_row(board: SudokuBoard, m, value):
    """
    Returns whether a value is legal for a row.
    @param board: A sudoku board. It contains the current position of a game.
    @param m: A row value in the range [0, ..., N).
    @param value: A value for a square.
    """
    row = []

    for n in range(board.N):
        row.append(board.get(m, n))

    return value not in row


def check_legal_column(board: SudokuBoard, n, value):
    """
    Returns whether a value is legal for a column.
    @param board: A sudoku board. It contains the current position of a game.
    @param n: A column value in the range [0, ..., N).
    @param value: A value for a square.
    """
    column = []

    for m in range(board.N):
        column.append(board.get(m, n))

    return value not in column


def check_legal_region(board: SudokuBoard, m, n, value):
    """
    Returns whether a value is legal for a region.
    @param board: A sudoku board. It contains the current position of a game.
    @param m: A row value in the range [0, ..., N).
    @param n: A column value in the range [0, ..., N).
    @param value: The number that we want to put on the board
    """
    row_region_index = (m // board.m) * board.m
    column_region_index = (n // board.n) * board.n
    region = []

    for m_i in range(row_region_index, row_region_index + board.m):
        for n_i in range(column_region_index, column_region_index + board.n):
            region.append(board.get(m_i, n_i))

    return value not in region


def is_empty_cell(board: SudokuBoard, m, n):
    """
    Checks if current coordinate is empty (has value 0).
    @param board: A sudoku board. It contains the current position of a game.
    @param m: A row value in the range [0, ..., N)
    @param n: A column value in the range [0, ..., N)
    """
    return board.get(m, n) == 0


def is_legal_move(game_state: GameState, m, n, value):
    """
    Checks if the current move would disqualify you from the game
    @param game_state: The current game state of type GameState
    @param m: A row value in the range [0, ..., N)
    @param n: A column value in the range [0, ..., N)
    @param value: A value in the range [1, ..., N]
    """
    move = TabooMove(m, n, value)
    return move not in game_state.taboo_moves and \
        check_legal_row(game_state.board, m, value) and \
        check_legal_column(game_state.board, n, value) and \
        check_legal_region(game_state.board, m, n, value)


def get_legal_moves(game_state: GameState):
    """
    A method to calculate all legal moves from a GameState return a list of legal moves.
    @param game_state: The current game state of type GameState.
    """
    legal_moves = []

    # Go over all possible index combination of the board
    for i in range(game_state.board.N):
        for j in range(game_state.board.N):
            # if the cell is not empty we can skip evaluating values
            if not is_empty_cell(game_state.board, i, j):
                continue
            else:
                # Try all possible values [1, ..., N] for a cell
                for k in range(1, game_state.board.N + 1):
                    # If a move is legal append to list of legal moves
                    if is_legal_move(game_state, i, j, k):
                        legal_moves.append(Move(i, j, k))

    return legal_moves


def calculate_new_game_state(game_state: GameState, move: Move):
    new_game_state = copy.deepcopy(game_state)
    new_game_state.board.put(move.i, move.j, move.value)
    new_game_state.moves.append(move)
    # TODO: Does not update potential GameState scores, it's not needed yet but might want to look into that
    return new_game_state
