from competitive_sudoku.sudoku import SudokuBoard, TabooMove


def check_complete_square(state, i, j, rows, cols):
    '''
    Checks if the move completes a square
    :param state: GameState class
    :param i: A row value in the range [0, ..., N)
    :param j: A column value in the range [0, ..., N)
    :param rows: Integer representing the number of rows in a block
    :param cols: Integer representing the number of columns in a block
    :return: Boolean indicating if the square is completed by the move
    '''
    squareRow, squareCol = rows * (i // rows), cols * (j // cols)
    # Check the squares for empty values
    for p in range(squareRow, squareRow + rows):
        for q in range(squareCol, squareCol + cols):
            # Skip over the potential move
            if p == i and q == j:
                continue
            elif state.board.get(p, q) == SudokuBoard.empty:
                return False
    return True


def check_complete_row(state, i, j):
    '''
    Checks if the move completes a row
    :param state: GameState class
    :param i: A row value in the range [0, ..., N)
    :param j: A column value in the range [0, ..., N)
    :return: Boolean indicating if the row is completed by the move
    '''
    N = state.board.N
    for x in range(N):
        # Skip over the potential move
        if j == x:
            continue
        elif state.board.get(i, x) == SudokuBoard.empty:
            return False
    return True


def check_complete_col(state, i, j):
    '''
    Checks if the move completes a column
    :param state: GameState class
    :param i: A row value in the range [0, ..., N)
    :param j: A column value in the range [0, ..., N)
    :return: Boolean indicating if the column is completed by the move
    '''
    N = state.board.N
    for x in range(N):
        # Skip over the potential move
        if i == x:
            continue
        elif state.board.get(x, j) == SudokuBoard.empty:
            return False
    return True


def evaluate_move(move, state):
    '''
    Generate the score of a move based on the rules of the game
    :param move: Move class
    :param state: gameState class
    :return: An integer based on the scoring of the game
    '''
    rows = state.board.m
    cols = state.board.n
    i = move.i
    j = move.j

    completed = 0
    if check_complete_square(state, i, j, rows, cols):
        completed = completed + 1
    if check_complete_row(state, i, j):
        completed = completed + 1
    if check_complete_col(state, i, j):
        completed = completed + 1

    return (2 ** completed - 1)


def possible(i, j, value, state, rows, cols, N):
    '''
    Checks if the move is possible
    :param i: A row value in the range [0, ..., N)
    :param j: A column value in the range [0, ..., N)
    :param value: A value in the range [1, ..., N]
    :param state: gameState class
    :param rows: Integer representing the number of rows in a block
    :param cols: Integer representing the number of columns in a block
    :param N: Integer representing the number of cols and rows
    :return:
    '''
    squareRow, squareCol = rows * (i // rows), cols * (j // cols)

    # Check the squares for same value
    for p in range(squareRow, squareRow + rows):
        for q in range(squareCol, squareCol + cols):
            if state.board.get(p, q) == value:
                return False

    # Check the rows and column for the same value
    for x in range(N):
        if state.board.get(i, x) == value:
            return False
        elif state.board.get(x, j) == value:
            return False

    return (state.board.get(i, j) == SudokuBoard.empty and not TabooMove(i, j, value) in state.taboo_moves)
