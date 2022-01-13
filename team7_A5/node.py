from __future__ import annotations
from competitive_sudoku.sudoku import GameState, Move, SudokuBoard, TabooMove
from copy import deepcopy
import logging
from dataclasses import dataclass, field
from typing import Any, Callable, ClassVar, Dict, Optional, List, Union


@dataclass
class MoveData:
    """Stores data to be stored and loaded"""
    move: Move = Move(0, 0, 0)
    value: int = 0
    priority: int = 0
    board: SudokuBoard = None
    score: int = 0

    def update(self) -> None:
        pass


class Node:
    def __init__(self, data: MoveData, is_root=False, dummy=False, is_cur=False):
        """

        """
        self.root = None
        self.parent = None
        self.depth = None
        self.score = None
        self.data = data
        self.children = []
        self.is_root = False
        if is_root:
            self.depth = 1
            self.root = self
            self.is_root = True
        if is_cur:
            self.value = data.value
        if dummy:
            pass

    def is_leaf(self) -> bool:
        return bool(self.children)

    def is_root(self) -> bool:
        return self.is_root

    def is_cur(self):
        return bool(self.parent)

    def add_child(self, node_data) -> None:
        """
        Add a Node child to self.Node
        :param node_data:
        :return: Updates self.Node.children
        """
        child = Node(node_data)
        child.depth = self.depth + 1
        child.root = self.root
        child.parent = self
        self.children.append(child)

    def minimax(self, t_moves, to_add) -> None:
        to_add.sort(key=lambda node: node.priority)

    def get_children(self) -> List[Node]:
        """
        :return: List of children of self.Node of size [0 ... self.board.n_empty]
        """
        return self.children

    def add_score(self, score: Union[float, int]) -> None:
        # TODO bleh
        pass

    def eval(self) -> int:
        # TODO make an evaluation function
        pass

    def calc_priority(self) -> int:
        # TODO  make priority function
        pass

    def add_layer(self):
        pass
