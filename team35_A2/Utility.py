import random
from team35_A2.Evaluation import possible
from competitive_sudoku.sudoku import Move, SudokuBoard
from team35_A2.Solver import solve_sudoku
import copy


def split(lst, length):
    '''
    Transformes the list of value of the board to a tuple containing the
    rows of values
    :param lst: list containing all the value of the board
    :param length: the number of rows
    :return: A tuple representing the values of the rows on the board

    Example
    split([1,2,3,4],2)
    >> ([1,2],[3,4])
    '''
    k, m = divmod(len(lst), length)
    return (lst[i * k + min(i, m):(i + 1) * k + min(i + 1, m)]
            for i in range(length))


def random_move(N, m, n, state):
    '''
    Returns a random legal move
    :param N: Integer representing the total number of cols and rows
    :param m: Integer representing the number of rows in a block
    :param n: Integer representing the number of columns in a block
    :param state: GameState Class
    :return: Move class
    '''
    # Initiate lists of the indexes of the rows and columns and the possible values
    rows = list(range(N))
    cols = list(range(N))
    values = list(range(1, N + 1))

    # Shuffle every list to randomize the move
    random.shuffle(rows)
    random.shuffle(cols)
    random.shuffle(values)

    # Iterate over the lists until random move is found
    for row in rows:
        for col in cols:
            for value in values:
                if possible(row, col, value, state, m, n, N):
                    return Move(row, col, value)


def no_solution_move(N, m, n, state):
    '''
    Returns a move that will lead to no solution of the sudoku
    :param N: Integer representing the total number of cols and rows
    :param m: Integer representing the number of rows in a block
    :param n: Integer representing the number of columns in a block
    :param state: GameState Class
    :return: Move class
    '''
    # Iterate over all the rows, columns, and possible values
    for i in range(N):
        for j in range(N):
            for v in range(1, N + 1):
                if possible(i, j, v, state, m, n, N):
                    # Initiate a copy state and perform the move
                    tempState = copy.deepcopy(state)
                    tempState.board.put(i, j, v)

                    # Format needed for the sudoku solver
                    test = list(split(tempState.board.squares, N))

                    # If the sudoku is still solvable, not the right move and continue iterating
                    if solve_sudoku(test, 0, 0, n, m)[0]:
                        continue
                    else:  # If no longer solvable, play this move
                        return True, Move(i, j, v)
    return False, Move(-1, -1, -1)  # Return false and no move if there is not such a move
