import random
from competitive_sudoku.sudoku import GameState, Move, SudokuBoard, TabooMove
import copy
from team35_A1.Evaluation import evaluate_move, possible


class MiniMaxAlphaBeta(object):
    '''
    A simple class for the minimax algorithm
    '''

    def __init__(self, maxDepth, player):
        '''
        Constructs an agent
        :param maxDepth: The amount of moves it wants to calculate in advance
        :param player: an integer representing the player of the Minimax Agent
        '''
        self.maxDepth = maxDepth
        self.player = player

    def choose_action(self, state):
        '''
        Chooses the best action based on the maxDepth and the current state
        :param state: gameState class
        :return: An integer representing the evaluation score and the selected Move Class
        '''
        evalScore, selected = self.minimax(0, state, True, float('-inf'), float('inf'))
        return (evalScore, selected)

    def evaluation_function(self, state, player):
        '''
        Simple evaluation score based on the scoring of the game
        :param state: gameState Class
        :param player: An integer representing the player of the Minimax Agent
        :return: An integer representing the evaluation score
        '''
        if player == 1:
            return (state.scores[0] - state.scores[1])
        else:
            return (state.scores[1] - state.scores[0])

    def generate_moves(self, state):
        '''
        Generates the complete list of all legal moves
        :param state: gameState Class
        :return: A list with Move Classes
        '''
        N = state.board.N
        rows = state.board.m
        cols = state.board.n

        allMoves = [Move(i, j, value) for i in range(N) for j in range(N) for value in range(1, N + 1)
                    if possible(i, j, value, state, rows, cols, N)]

        return allMoves

    def minimax(self, currentDepth, state, is_max_turn, alpha, beta):
        '''
        The minimax algorithm with alpha beta pruning
        :param currentDepth: an integer representing moves played up to this point
        :param state: GameState Class
        :param is_max_turn: Boolean to indicate maximizing or minimizing
        :param alpha: Integer representing highest-value choice so far at any point along the max path.
        :param beta: Integer representing lowest-value choice so far at any point along the min path.
        :return: An integer representing the evaluation score and Move Class
        '''

        movesLeft = state.board.squares.count(SudokuBoard.empty)  # The amount of moves left

        # Terminate if it is either the maxDepth or if there are no moves left
        if currentDepth == self.maxDepth or movesLeft == 0:
            return self.evaluation_function(state, self.player), ""

        # Generate all the moves
        possibleAction = self.generate_moves(state)

        # Shuffle the moveset around for randomness
        random.shuffle(possibleAction)

        # Best value and best move has yet to be found
        bestValue = float('-inf') if is_max_turn else float('inf')
        actionTarget = ""

        # Iterate through the moveset
        for action in possibleAction:
            newState = copy.deepcopy(state)  # Copy current state
            newState.board.put(action.i, action.j, action.value)  # Play the new move

            # Calculate the score of the new move
            if is_max_turn and self.player == 1:
                newState.scores[0] = newState.scores[0] + evaluate_move(action, newState)
            elif is_max_turn and self.player == 2:
                newState.scores[1] = newState.scores[1] + evaluate_move(action, newState)
            elif (not is_max_turn) and self.player == 1:
                newState.scores[1] = newState.scores[1] + evaluate_move(action, newState)
            elif (not is_max_turn) and self.player == 2:
                newState.scores[0] = newState.scores[0] + evaluate_move(action, newState)

            # Do the same for the moves after this move
            eval_child, action_child = self.minimax(currentDepth + 1, newState, not is_max_turn, alpha, beta)

            # Maximize the value of the move
            if is_max_turn and bestValue < eval_child:
                bestValue = eval_child
                actionTarget = action
                alpha = max(alpha, bestValue)
                if beta <= alpha:  # Stop iterating over worse value moves
                    break

            # Minimize the value of the move
            elif (not is_max_turn) and bestValue > eval_child:
                bestValue = eval_child
                actionTarget = action
                beta = min(beta, bestValue)
                if beta <= alpha:  # Stop iterating over worsealue moves
                    break

        return bestValue, actionTarget
