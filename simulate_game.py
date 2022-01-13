#!/usr/bin/env python3

#  (C) Copyright Wieger Wesselink 2021. Distributed under the GPL-3.0-or-later
#  Software License, (See accompanying file LICENSE or copy at
#  https://www.gnu.org/licenses/gpl-3.0.txt)

import argparse
import importlib
import multiprocessing
import platform
import re
import time
import os
from pathlib import Path
from competitive_sudoku.execute import solve_sudoku
from competitive_sudoku.sudoku import GameState, SudokuBoard, Move, TabooMove, load_sudoku_from_text
from competitive_sudoku.sudokuai import SudokuAI
import itertools
import logging

# LOGGER SETTINGS
logger = logging.getLogger("RUN2")
logger.setLevel(logging.DEBUG)

fh = logging.FileHandler('TESTRUN2.txt')
fh.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)

# add the handlers to the logger
logger.addHandler(fh)
logger.addHandler(ch)

def check_oracle(solve_sudoku_path: str) -> None:
    board_text = '''2 2
       1   2   3   4
       3   4   .   2
       2   1   .   3
       .   .   .   1
    '''
    output = solve_sudoku(solve_sudoku_path, board_text)
    result = 'has a solution' in output
    if result:
        print('The sudoku_solve program works.')
    else:
        print('The sudoku_solve program gives unexpected results.')
        print(output)


def simulate_game(initial_board: SudokuBoard, player1: SudokuAI, player2: SudokuAI, solve_sudoku_path: str, calculation_time: float = 0.5) -> int:
    """
    Simulates a game between two instances of SudokuAI, starting in initial_board. The first move is played by player1.
    @param initial_board: The initial position of the game.
    @param player1: The AI of the first player.
    @param player2: The AI of the second player.
    @param solve_sudoku_path: The location of the oracle executable.
    @param calculation_time: The amount of time in seconds for computing the best move.
    """
    import copy
    N = initial_board.N

    game_state = GameState(initial_board, copy.deepcopy(initial_board), [], [], [0, 0])
    move_number = 0
    number_of_moves = initial_board.squares.count(SudokuBoard.empty)
    print('Initial state')
    print(game_state)

    with multiprocessing.Manager() as manager:
        # use a lock to protect assignments to best_move
        lock = multiprocessing.Lock()
        player1.lock = lock
        player2.lock = lock

        # use shared variables to store the best move
        player1.best_move = manager.list([0, 0, 0])
        player2.best_move = manager.list([0, 0, 0])

        while move_number < number_of_moves:
            player, player_number = (player1, 1) if len(game_state.moves) % 2 == 0 else (player2, 2)
            print(f'-----------------------------\nCalculate a move for player {player_number}')
            player.best_move[0] = 0
            player.best_move[1] = 0
            player.best_move[2] = 0
            try:
                process = multiprocessing.Process(target=player.compute_best_move, args=(game_state,))
                process.start()
                time.sleep(calculation_time)
                lock.acquire()
                process.terminate()
                lock.release()
            except Exception as err:
                print('Error: an exception occurred.\n', err)
            i, j, value = player.best_move
            best_move = Move(i, j, value)
            print(f'Best move: {best_move}')
            player_score = 0
            if best_move != Move(0, 0, 0):
                if TabooMove(i, j, value) in game_state.taboo_moves:
                    print(f'Error: {best_move} is a taboo move. Player {3 - player_number} wins the game.')
                    return
                board_text = str(game_state.board)
                options = f'--move "{game_state.board.rc2f(i, j)} {value}"'
                output = solve_sudoku(solve_sudoku_path, board_text, options)
                if 'Invalid move' in output:
                    print(f'Error: {best_move} is not a valid move. Player {3-player_number} wins the game.')
                    return
                if 'Illegal move' in output:
                    print(f'Error: {best_move} is not a legal move. Player {3-player_number} wins the game.')
                    return
                if 'has no solution' in output:
                    print(f'The sudoku has no solution after the move {best_move}.')
                    player_score = 0
                    game_state.moves.append(TabooMove(i, j, value))
                    game_state.taboo_moves.append(TabooMove(i, j, value))
                if 'The score is' in output:
                    match = re.search(r'The score is ([-\d]+)', output)
                    if match:
                        player_score = int(match.group(1))
                        game_state.board.put(i, j, value)
                        game_state.moves.append(best_move)
                        move_number = move_number + 1
                    else:
                        raise RuntimeError(f'Unexpected output of sudoku solver: "{output}".')
            else:
                print(f'No move was supplied. Player {3-player_number} wins the game.')
                return
            game_state.scores[player_number-1] = game_state.scores[player_number-1] + player_score
            print(f'Reward: {player_score}')
            print(game_state)
        if game_state.scores[0] > game_state.scores[1]:
            print('Player 1 wins the game.')
            return 1
        elif game_state.scores[0] == game_state.scores[1]:
            print('The game ends in a draw.')
            return 2
        elif game_state.scores[0] < game_state.scores[1]:
            print('Player 2 wins the game.')
            return 3


def main():
    logger.info(f";time;board;player1;player2;iteratie;winner;winner_name")

    def custom_sim(time, p1, p2, board):
        solve_sudoku_path = 'bin\\solve_sudoku.exe' if platform.system() == 'Windows' else 'bin/solve_sudoku'
        board_text = Path("boards\\" + board).read_text()
        board = load_sudoku_from_text(board_text)

        module1 = importlib.import_module(p1 + '.sudokuai')
        module2 = importlib.import_module(p2 + '.sudokuai')
        player1 = module1.SudokuAI()
        player2 = module2.SudokuAI()
        player1.player_number = 1
        player2.player_number = 2
        if p1 in ('random_player', 'greedy_player', 'random_save_player'):
            player1.solve_sudoku_path = solve_sudoku_path
        if p2 in ('random_player', 'greedy_player', 'random_save_player'):
            player2.solve_sudoku_path = solve_sudoku_path

        # clean up files
        if os.path.isfile(os.path.join(os.getcwd(), '-1.pkl')):  # Check if there actually is something
            os.remove(os.path.join(os.getcwd(), '-1.pkl'))
        if os.path.isfile(os.path.join(os.getcwd(), '1.pkl')):  # Check if there actually is something
            os.remove(os.path.join(os.getcwd(), '1.pkl'))
        if os.path.isfile(os.path.join(os.getcwd(), '2.pkl')):  # Check if there actually is something
            os.remove(os.path.join(os.getcwd(), '2.pkl'))

        winner = simulate_game(board, player1, player2, solve_sudoku_path=solve_sudoku_path, calculation_time=time)
        return winner

    time = [0.1, 0.2, 0.3, 0.5, 1, 5]
    players = ["team7_A2", "team7_A3", "team7_A6", "greedy_player"]
    combis = list(itertools.combinations(players, 2))
    player1 = []
    player2 = []
    for combi in combis:
        player1.append(combi[0])
        player1.append(combi[1])
        player2.append(combi[1])
        player2.append(combi[0])
    boards = ["empty-2x2.txt", "empty-3x3.txt", "easy-3x3.txt", "random-3x3.txt", "hard-3x3.txt", "empty-4x4.txt", "random-4x4.txt"]
    N = 5

    # time = [0.5, 1]
    # players = ["team7_A2", "team7_A6"]
    # combis = list(itertools.combinations(players, 2))
    # player1 = []
    # player2 = []
    # for combi in combis:
    #     player1.append(combi[0])
    #     player1.append(combi[1])
    #     player2.append(combi[1])
    #     player2.append(combi[0])
    # boards = ["empty-2x2.txt",  "easy-3x3.txt"]
    # N = 2

    for t in time:
        for board in boards:
            for p1, p2 in zip(player1, player2):
                for i in range(N):
                    winner = custom_sim(t, p1, p2, board)
                    print(winner)
                    if winner == 1:
                        winner_name = p1
                    elif winner == 2:
                        winner_name = "draw"
                    else:
                        winner_name = p2
                    logger.info(f";{t};{board};{p1};{p2};{i};{winner};{winner_name}")



if __name__ == '__main__':
    main()
