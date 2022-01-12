from competitive_sudoku.sudoku import GameState, Move, SudokuBoard, TabooMove


def evaluate_move(move, state):
    '''
    Generate the score of a move based on the rules of the game
    :param move: Move class
    :param state: gameState class
    :return: An integer based on the scoring of the game
    '''
    N = state.board.N
    rows = state.board.m
    cols = state.board.n
    i = move.i
    j = move.j

    squareRow, squareCol = rows * (i // rows), cols * (j // cols)
    completed = 3
    # Check the squares for empty values
    for p in range(squareRow, squareRow + rows):
        for q in range(squareCol, squareCol + cols):
            # Skip over the potential move
            if p == i and q == j:
                continue
            elif state.board.get(p, q) == SudokuBoard.empty:
                completed = 2
                break

    # Check the rows for empty values
    for x in range(N):
        # Skip over the potential move
        if j == x:
            continue
        elif state.board.get(i, x) == SudokuBoard.empty:
            completed = completed - 1
            break
    # Check the columns for empty values
    for x in range(N):
        # Skip over the potential move
        if i == x:
            continue
        elif state.board.get(x, j) == SudokuBoard.empty:
            completed = completed - 1
            break

    return (2 ** completed - 1)


def possible(i, j, value, state, rows, cols, N):
    '''
    Checks if the move is possible
    :param i: A row value in the range [0, ..., N)
    :param j: A column value in the range [0, ..., N)
    :param value: A value in the range [1, ..., N]
    :param state: gameState class
    :return: Boolean indicating if the move is legal
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
