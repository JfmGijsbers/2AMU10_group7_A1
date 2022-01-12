import random
from competitive_sudoku.sudoku import SudokuBoard, Move
import copy
from team35_A2.Evaluation import evaluate_move
from team35_A2.Utility import split
from team35_A2.Solver import solve_sudoku
import numpy as np


class MiniMaxAlphaBeta(object):
    '''
    A simple class for the minimax algorithm
    '''

    def __init__(self, maxDepth, player, state):
        '''
        Constructs an agent
        :param maxDepth: The amount of moves it wants to calculate in advance
        :param player: an integer representing the player of the Minimax Agent
        :param state: GameState class
        '''
        self.maxDepth = maxDepth
        self.player = player
        self.root = Node(state, [])

    def choose_action(self):
        '''
        Chooses the best action based on the maxDepth and the current state
        :param state: gameState class
        :return: An integer representing the evaluation score and the selected Move Class
        '''
        evalScore, selected = self.minimax(0, True,
                                           float('-inf'), float('inf'), self.root)
        return (evalScore, selected)

    def evaluation_early(self, state):
        '''
        Early game evaluation to delay points scored in the game
        :param state: GameState class
        :return: An integer representing the evaluation score
        '''

        N = state.board.N
        # Initiate empty array equal to the board size
        x = np.zeros((N, N))
        for i in range(0, N):
            for j in range(0, N):
                if state.board.get(i, j) == SudokuBoard.empty:
                    # Fill in the score of a move on the board
                    x[i, j] = evaluate_move(Move(i, j, -1), state)

        # Minimize the number of possible scoring opportunities on the board
        return (-np.mean(x))

    def evaluation_late(self, state, player):
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
        # Format needed for the sudoku solver
        board = list(split(state.board.squares, state.board.N))
        rows = state.board.m
        cols = state.board.n

        # Solve sudoku to get the list of moves
        allMoves = solve_sudoku(board, 0, 0, cols, rows)[1]

        return allMoves

    def minimax(self, currentDepth, is_max_turn, alpha, beta, child):
        '''
        The minimax algorithm with alpha beta pruning
        :param currentDepth: an integer representing moves played up to this point
        :param is_max_turn: Boolean to indicate maximizing or minimizing
        :param alpha: Integer representing highest-value choice so far at any point along the max path.
        :param beta: Integer representing lowest-value choice so far at any point along the min path.
        :param child: Node Class
        :return: An integer representing the evaluation score and Move Class
        '''

        # Setting parameters
        state = child.get_state()
        movesLeft = state.board.squares.count(SudokuBoard.empty)  # The amount of moves left
        squares = state.board.N ** 2

        # Terminate if it is either the maxDepth or if there are no moves left
        # Early game strategy if there is more than 1/3 empty spaces
        if currentDepth == self.maxDepth and movesLeft > (squares / 3):
            return self.evaluation_early(state), ""
        elif currentDepth == self.maxDepth or movesLeft == 0:  # Late game strategy
            return self.evaluation_late(state, self.player), ""

        # Generate all the moves and the children nodes for the root nodes
        # in the first layer of iterative deepening
        if currentDepth == 0 and len(child.get_moves()) == 0:
            possibleAction = self.generate_moves(state)
            random.shuffle(possibleAction)
            self.root.moves = possibleAction
            self.root.generate_children(is_max_turn, self.player, child)

        # Generate children nodes for nodes beside the root node
        # Only happens once for each child
        if len(child.get_children()) == 0:
            child.generate_children(is_max_turn, self.player, child)

        # Best value and best move has yet to be found
        bestValue = float('-inf') if is_max_turn else float('inf')
        actionTarget = ""

        # Iterate over all the children nodes
        for i in range(len(child.get_children())):
            c = child.get_children()[i]
            # Recursion over the next nodes
            eval_child, action_child = self.minimax(currentDepth + 1, not is_max_turn,
                                                    alpha, beta, c)

            # Maximize the value of the move
            if is_max_turn and bestValue < eval_child:
                bestValue = eval_child
                actionTarget = c.action
                alpha = max(alpha, bestValue)
                if beta <= alpha:  # Stop iterating over worse value moves
                    # Put the child in front for the next layer of deepening to possible have the cut earlier
                    child.swap_child(0, i)
                    break

            # Minimize the value of the move
            elif (not is_max_turn) and bestValue > eval_child:
                bestValue = eval_child
                actionTarget = c.action
                beta = min(beta, bestValue)
                if beta <= alpha:  # Stop iterating over worse value moves
                    # Put the child in front for the next layer of deepening to possible have the cut earlier
                    child.swap_child(0, i)
                    break

        return bestValue, actionTarget


class Node(object):
    '''
    A class to construct nodes in the minimax tree
    '''

    def __init__(self, state, children, moves=[], parent=None, action=None):
        '''
        :param state: GameState class
        :param children: List containing node classes
        :param moves: List containing Move classes which are possible in the current state
        :param parent: A node class that represent the previous node in the tree
        :param action: Move performed on the state
        '''
        self.children = children
        self.state = state
        self.parent = parent
        self.moves = moves
        self.action = action

    def get_state(self):
        '''
        Obtain the state of the node
        :return: Gamestate Class
        '''
        return self.state

    def get_children(self):
        '''
        Obtain the list of children nodes
        :return: List containing node classes
        '''
        return self.children

    def get_moves(self):
        '''
        Obtain the possible moves
        :return: List containing Move classes
        '''
        return self.moves

    def generate_children(self, is_max_turn, player, parent):
        '''
        Generate the node Classes for all possible moves at the current state
        :param is_max_turn: Boolean to indicate maximizing or minimizing
        :param player: an integer representing the player of the Minimax Agen
        :param parent: Node class
        :return:
        '''
        for index in range(len(self.moves)):
            action = self.moves[index]
            newState = copy.deepcopy(self.state)  # Copy current state
            newState.board.put(action.i, action.j, action.value)  # Play the new move

            # Calculate the score of the new move
            if is_max_turn and player == 1:
                newState.scores[0] = newState.scores[0] + evaluate_move(action, newState)
            elif is_max_turn and player == 2:
                newState.scores[1] = newState.scores[1] + evaluate_move(action, newState)
            elif (not is_max_turn) and player == 1:
                newState.scores[1] = newState.scores[1] + evaluate_move(action, newState)
            elif (not is_max_turn) and player == 2:
                newState.scores[0] = newState.scores[0] + evaluate_move(action, newState)

            # The remaining moves are all moves of parent without played move
            remainingMoves = self.moves[:index] + self.moves[index + 1:]

            # Add child to the list of children
            self.add_child(Node(newState, [], remainingMoves, parent, action))

    def add_child(self, node):
        '''
        Add the child Node to the list of children
        :param node: Node Class
        '''
        self.children.append(node)

    def swap_child(self, new, original):
        '''
        Change the position of a child in the list
        :param new: new position in the list
        :param original: original position in the list
        '''
        self.children.insert(new, self.children.pop(original))
