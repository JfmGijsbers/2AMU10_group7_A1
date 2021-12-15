from competitive_sudoku.sudoku import GameState, Move
from team7_A2.evaluate import evaluate
from copy import deepcopy

import logging
log = logging.getLogger("sudokuai")
log.setLevel(logging.DEBUG)


class Node:
    def __init__(self, game_state, move, our_move):
        self.move = move
        self.game_state = game_state
        self.new_game_state = self.update_gamestate(game_state)
        self.children = []
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

    def calculate_children(self, root, all_moves: list, our_move: bool):
        for move in all_moves:
            new_game_state = deepcopy(root.game_state)
            new_move = deepcopy(move)
            node = Node(new_game_state, new_move, not our_move)
            if not node.taboo:
                self.add_child(node)

    def update_gamestate(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.board.put(self.move.i, self.move.j, self.move.value)
        new_game_state.moves.append(self.move)
        return new_game_state

    def has_children(self):
        return bool(self.children)

    def get_children(self):
        return self.children
