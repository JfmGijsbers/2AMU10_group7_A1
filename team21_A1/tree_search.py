from team21_A1.helper_functions import get_legal_moves, calculate_new_game_state
from team21_A1.evaluation import evaluate_move
from competitive_sudoku.sudoku import GameState, Move


class Node:
    def __init__(self, score: int = None, move: Move = None, game_state: GameState = None, father=None, our_move=True):
        self.score = score
        self.move = move
        self.game_state = game_state
        self.father = father
        self.children = []
        self.our_move = our_move

    def add_child(self, child):
        self.children.append(child)

    def get_children(self):
        return self.children

    def is_leaf(self):
        return self.children == []

    def node_score(self):
        return self.score

    def evaluate(self):
        self.score = evaluate_move(self.game_state, self.move, self.our_move, self.score)


# There should be a tree for every (currently possible) move, not just one tree for all moves
# This is both easier, and allows us to check which move is best by accessing the root (instead of through parent)
class Tree:
    def __init__(self, root_moves, cur_game_state, init_score):
        self.root = []
        self.init_score = init_score
        for cur_move in root_moves:
            new_game_state = calculate_new_game_state(cur_game_state, cur_move)
            cur_node = Node(score=init_score, move=cur_move, game_state=new_game_state)
            cur_node.evaluate()

            self.root.append(cur_node)

    def add_layer(self):
        for node in self.root:
            self.add_children(node)

    def add_children(self, parent_node: Node):
        # Recursively find leaf nodes
        if len(parent_node.children) > 0:
            for child in parent_node.children:
                self.add_children(child)
        # This is a leaf node, so we need to expand it
        else:
            possible_moves = get_legal_moves(parent_node.game_state)

            for cur_move in possible_moves:

                cur_game_state = calculate_new_game_state(parent_node.game_state, cur_move)
                cur_node = Node(score=parent_node.score, move=cur_move, game_state=cur_game_state, father=parent_node)
                cur_node.evaluate()

                parent_node.add_child(cur_node)


# This is more for form than for functionality, could honestly be turned into loose functions like helper_functions.py
def find_best_move(tree):
    best_move = None
    best_score = -987654321
    for root_node in tree.root:
        root_node.score = alpha_beta_prune(root_node)
        if root_node.score > best_score:
            best_score = root_node.score
            best_move = root_node.move

    return best_move


def alpha_beta_prune(root_node: Node):
    alpha = -999999999
    beta = 999999999

    possible_moves = root_node.get_children()
    for move in possible_moves:
        score = min_beta(move, alpha, beta)
        if score > alpha:
            alpha = score
    return alpha


def min_beta(node: Node, alpha, beta):
    if node.is_leaf():
        return node.node_score()
    else:
        score = 999999999
        possible_moves = node.get_children()
        for move in possible_moves:
            score = min(score, max_alpha(move, alpha, beta))
            if score <= alpha:
                return score
            beta = min(beta, score)

    return score


def max_alpha(node: Node, alpha, beta):
    if node.is_leaf():
        return node.node_score()
    else:
        score = -999999999
        possible_moves = node.get_children()
        for move in possible_moves:
            score = max(score, min_beta(move, alpha, beta))
            if score >= beta:
                return score
            alpha = max(alpha, score)

    return score
