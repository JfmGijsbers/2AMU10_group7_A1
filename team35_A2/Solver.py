# Checks whether it will be legal to assign num to the given row, col
from competitive_sudoku.sudoku import Move
import random


def safe(grid, row, col, num, m, n):
    '''
    Checks whether it will be legal to assign num to the given row, col
    :param grid: A list representation of the board
    :param row: A row value in the range [0, ..., N)
    :param col: A column value in the range [0, ..., N)
    :param num: A value in the range [1, ..., N]
    :param m: The number of rows in a block.
    :param n: The number of columns in a block.
    :return: A boolean indicating if the num is appropriate in that place
    '''
    # Check if we find the same num in the row -> false
    N = len(grid)
    for x in range(N):
        if grid[row][x] == num:
            return False

    # Same for column -> false
    for x in range(N):
        if grid[x][col] == num:
            return False

    # Check if we find the same num in the square -> false
    startRow = row - row % int((N / m))
    startCol = col - col % int((N / n))
    for i in range(n):
        for j in range(m):
            if grid[i + startRow][j + startCol] == num:
                return False
    return True


def solve_sudoku(grid, row, col, m, n, list=[]):
    '''
    Fills in the sudoku to solve it
    :param grid: A list representation of the board
    :param row: A row value in the range [0, ..., N)
    :param col: A column value in the range [0, ..., N)
    :param m: The number of rows in a block.
    :param n: The number of columns in a block.
    :return: A boolean indicating if the sudoku is solvable and list with Move classes
    '''
    N = len(grid)
    # Check if we have reached the second to last row and last column to avoid
    # further backtracking
    if (row == N - 1 and col == N):
        return (True, list)

    # if column value becomes last column, move to next row
    if col == N:
        row += 1
        col = 0

    # Check if the current position of the grid already contains a value
    if grid[row][col] > 0:
        return solve_sudoku(grid, row, col + 1, m, n, list)
    for num in range(1, N + 1, 1):
        # Check if it is safe to place the value
        if safe(grid, row, col, num, m, n):
            # Assigning the value in the current position
            # Assumption -> assigned value is correct
            grid[row][col] = num
            # Checking for next possibility with next column
            if solve_sudoku(grid, row, col + 1, m, n, list)[0]:
                list.append(Move(row, col, num))
                return (True, list)

        # Assumption was wrong -> Removing the assigned value
        grid[row][col] = 0
    return (False, [])
