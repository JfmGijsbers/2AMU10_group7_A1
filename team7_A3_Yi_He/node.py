from __future__ import annotations
from competitive_sudoku.sudoku import GameState, Move
from team7_A3_Yi_He.evaluate import evaluate
from copy import deepcopy
from typing import List, Union
import logging


class Node:
    def __init__(self, move: Move, is_root=False):
        """
        """
        self.depth = None
        self.root = None
        self.parent = None
        self.move = move
        self.value = self.eval()
        self.children = []
        if is_root:
            self.depth = 0
            self.root = move

    def is_leaf(self) -> bool:
        return bool(self.children)

    def is_root(self) -> bool:
        return bool(self.parent)

    def add_child(self, move) -> None:
        """
        Add a Node child to self.Node
        :param move:
        :return: Updates self.Node.children
        """
        child = Node(move)
        child.depth = self.depth + 1
        child.root = self.root
        child.parent = self
        self.children.append(child)

    def get_children(self) -> List[Node]:
        """
        :return: List of children of self.Node of size [0 ... self.board.n_empty]
        """
        return self.children

    def add_score(self, score: Union[float, int]) -> None:
        # TODO bleh
        self.score = score

    def eval(self) -> int:
        # TODO make an evaluation function
        pass
