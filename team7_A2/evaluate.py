import copy
from competitive_sudoku.sudoku import Move, SudokuBoard, GameState, TabooMove
from typing import List
import logging
log = logging.getLogger("sudokuai")

CHECKS = {
    "INVALID": 0,
    "VALID": 1,
    "SCORING": 2
}
SCORES = [0, 1, 3, 7]

def check_row(board: SudokuBoard, move: Move) -> bool:
    row = [board.get(move.i, k) for k in range(board.N) if k != move.j]
    if move.value in row:
        log.debug(f"Move invalid for row: {str(move)}")
        return CHECKS["INVALID"]
    elif 0 in row:
        log.debug(f"Move valid for row: {str(move)}")
        return CHECKS["VALID"]
    else:
        log.debug(f"Move scoring for row: {str(move)}")
        return CHECKS["SCORING"]

def check_column(board: SudokuBoard, move: Move) -> bool:
    column = [board.get(k, move.j) for k in range(board.N) if k != move.i]
    log.debug(f"Evaluating move {move}")
    for val in column:
        log.debug(f"val in col {move.j} is {val}")
    if move.value in column:
        log.debug(f"Move invalid for column: {str(move)}")
        return CHECKS["INVALID"]
    elif 0 in column:
        log.debug(f"Move valid for column: {str(move)}")
        return CHECKS["VALID"]
    else:
        log.debug(f"Move scoring for column: {str(move)}")
        return CHECKS["SCORING"]

def check_square(board: SudokuBoard, move: Move) -> bool:
    values = []
    m = board.m
    n = board.n
    column = move.i // m
    row = move.j // n
    for i in range(m):
        # then each column
        for j in range(n):
            curr = board.get( n * column + j, m * row + i)
            # Do we have an empty cell?
            if curr == 0:
                # Is this empty cell the move we currently want to make?
                if m * row + i == move.j and n * column + j == move.i:
                    log.debug(f"[{n * column + j}, {m * row + i}] for move {move}")
                    pass
                else:
                    values.append(curr)
            else:
                values.append(curr)
    if move.value in values:
        log.debug(f"Move invalid for square: {str(move)}")
        return CHECKS["INVALID"]
    elif 0 in values:
        log.debug(f"Move valid for square: {str(move)}")
        return CHECKS["VALID"]
    else:
        log.debug(f"Move scoring for square: {str(move)}")
        return CHECKS["SCORING"]

def get_all_moves(game_state: GameState) -> List[Move]:
    """
    Returns a list of all possible moves
    :param game_state: a game state
    :return: a list of moves
    """
    N = game_state.board.N
    all_moves = []
    for i in range(N):
        for j in range(N):
            # We don't need to look at all possible values if we already know that the cell is occupied
            if not is_empty(game_state.board, i, j):
                #log.debug(f"[{i}, {j}] is not possible")
                pass
            else:
                for value in range(1, N+1):
                    curr = Move(i, j, value)
                    log.debug(f"Move {curr} has value {evaluate(game_state, curr)}")
                    if evaluate(game_state, curr) == -1:
                        pass
                    else:
                        all_moves.append(curr)
    log.debug(f"get_all_moves returned {str(len(all_moves))} moves")
    return all_moves

def is_empty(board: SudokuBoard, m, n):
    log.debug(f"[{m}, {n}] has value {board.get(m,n)}")
    return board.get(m, n) == 0

def evaluate(game_state: GameState, move: Move):
    """
    Evaluates a single move and returns a score
    :param game_state: a game state
    :param move: a move
    :return: score
    """

    scores = 0
    col = check_column(game_state.board, move)
    if col == CHECKS["INVALID"]:
        return -1
    else:
        if col == CHECKS["SCORING"]:
            scores += 1
        row = check_row(game_state.board, move)
        if row == CHECKS["INVALID"]:
            return -1
        else:
            if row == CHECKS["SCORING"]:
                scores += 1
            square = check_square(game_state.board, move)
            if square == CHECKS["INVALID"]:
                return -1
            else:
                if square == CHECKS["SCORING"]:
                    scores += 1
    log.info(f"Score {str(SCORES[scores])} for move {str(move)}")
    return SCORES[scores]