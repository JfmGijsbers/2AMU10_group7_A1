from competitive_sudoku.sudoku import GameState, Move
from team7_A2.evaluate import evaluate
from copy import deepcopy

import logging
log = logging.getLogger("sudokuai")
log.setLevel(logging.DEBUG)

class Node:
    def __init__(self, game_state, move, our_move):
        self.root_move = None
        self.game_state = game_state
        self.children = []
        self.move = move
        self.our_move = our_move
        self.taboo = False
        self.value = self.calc_value()

    def calc_value(self):
        val = evaluate(self.game_state, self.move)
        if val == -1:
            self.taboo = True
        if not self.our_move:
            val *= -1
        return val

    def add_child(self, node):
        self.children.append(node)

    def calculate_children(self, root, all_moves: list, our_move: bool, depth = 2):
        for move in all_moves:
            new_game_state = deepcopy(root.game_state)
            new_move = deepcopy(move)
            node = Node(new_game_state, new_move, not our_move)
            #log.info(f"Node with move {move} has value {node.value}")
            if not node.taboo:
                if depth == 1:
                    log.critical(f"Found root move {root.move}")
                    node.root_move = new_move
                else:
                    log.critical(f"Copied root {root.root_move}")
                    node.root_move = root.root_move
                self.add_child(node)

    def update_gamestate(self):
            self.game_state.board.put(self.move.i, self.move.j, self.move.value)
            self.game_state.moves.append(self.move)

    def has_children(self):
        return bool(self.children)

    def get_children(self):
        return self.children

