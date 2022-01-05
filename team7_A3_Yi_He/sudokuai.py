#  (C) Copyright Wieger Wesselink 2021. Distributed under the GPL-3.0-or-later
#  Software License, (See accompanying file LICENSE or copy at
#  https://www.gnu.org/licenses/gpl-3.0.txt)

import random
import math
from typing import Union, Tuple
from competitive_sudoku.sudoku import GameState, Move
import competitive_sudoku.sudokuai
from team7_A3.evaluate import evaluate
from team7_A3.node import Node
from team7_A3.strategies import get_all_moves, get_strategy
from copy import deepcopy
import logging

log = logging.getLogger("sudokuai")


class SudokuAI(competitive_sudoku.sudokuai.SudokuAI):
    """
    Sudoku AI that computes a move for a given sudoku configuration.
    """

    # TODO prioritise -> Yi He 2e
    # TODO skip turn -> Yi He 1e
    # TODO strategies -> 5e
    # TODO pick strategies depending on the game state phase
    # TODO horizontale random choice fixen (in minimax door de min en max) -> Yi He
    # TODO snelle agent -> Jeroen
    # TODO optimaliseren (sneller) gebruik van eerder gemaakte variablen bij andere functies -> Yi He 3e
    # TODO save load -> Yi He 4e
    # TODO verslag -> Sander
    # TODO code anderen -> Sander

    def __init__(self):
        super().__init__()

    def compute_best_move(self, game_state: GameState) -> None:
        """
        Computes the best move
        :param game_state: the game_state
        :return:
        """
        # Save data
        # self.save(test_data)

        # Load data
        # saved_data = self.load()

        is_maximising_player = True

        # Determine which strategies to play
        strategies = get_strategy(game_state)

        # Calculate the first layer of moves depending on the given strategies
        all_moves = get_all_moves(game_state, strategies)
        if len(all_moves) == 0:
            log.error("No moves found!")

        # Always have a move proposed
        try:
            self.propose_move(random.choice(all_moves))
        except:
            log.critical("Not proposing any moves")
            return

        # Instantiate the root of the game tree
        root_move = Move(0, 0, 0)
        depth = 0
        root = Node(game_state, root_move, False, depth)

        # Compute layer 1 by calculating the children of the root
        depth = depth + 1
        root.calculate_children(all_moves)
        # Obtain the best move from the minimax
        random.shuffle(root.children)
        best_move = self.minimax(root, depth, -math.inf, math.inf, False)
        print("finished layer 1")
        self.propose_move(best_move.root_move)

        # switch turns
        is_maximising_player = not is_maximising_player

        # ITERATIVE DEEPENING
        # Keep computing moves as long as there are moves to make,
        # alternating between our and the opponent's turn
        children = root.children
        while len(children) != 0:
            leaves = []
            depth += 1
            # calculate new layer
            for child in children:
                strategies = get_strategy(child.game_state)
                cand_leaves = get_all_moves(child.game_state, strategies)
                child.calculate_children(cand_leaves)
                for leaf in child.children:
                    leaves.append(leaf)
            children = leaves
            random.shuffle(children)
            # calculate best move
            if len(children) != 0:
                best_move = self.minimax(root, depth, -math.inf, math.inf, False)
                self.propose_move(best_move.root_move)
                is_maximising_player = not is_maximising_player
                print(f"finished layer {depth}")
            else:
                print("FINISHED TREE")

    def minimax(self, node: Node, depth: int, alpha: Union[float, int], beta: Union[float, int],
                is_maximising_player: bool) -> Tuple[Node, int]:
        """
        Recursively evaluates nodes in game tree and returns the proposed best node.
        Proposed best node is the node that has either the maximum or the mimimum value in the terminal state
        depending if is_maximising_player is True or False respectively.
        :param node: starting state
        :param depth: terminal search depth
        :param alpha: pruning
        :param beta: pruning
        :param is_maximising_player: is maximising player?
        :param score: current score
        :return: best node proposal
        """
        if depth == 0:
            node.add_score(node.value)
            return node

        children = deepcopy(node.children)
        if is_maximising_player or node.depth == 0:
            # deep copy node, since it has to be a node object to compare
            maxValue = deepcopy(node)
            maxValue.add_score(-math.inf)
            # assign -inf value to the node
            for child in children:
                if node.depth == 0:
                    value = self.minimax(child, depth - 1, alpha, beta, True)
                else:
                    value = self.minimax(child, depth - 1, alpha, beta, False)
                random_boolean = bool(random.getrandbits(1))
                if random_boolean:
                    maxValue = max([maxValue, value], key=lambda state: state.score)
                else:
                    maxValue = max([value, maxValue], key=lambda state: state.score)
                alpha = max(maxValue.score, alpha)
                if beta <= alpha:
                    break
            maxValue.add_score(maxValue.score + node.value)
            return maxValue
        else:
            # minimizing player, similar to the maximising player
            minValue = deepcopy(node)
            minValue.add_score(math.inf)
            for child in children:
                value = self.minimax(child, depth - 1, alpha, beta, True)
                random_boolean = bool(random.getrandbits(1))
                if random_boolean:
                    minValue = min([minValue, value], key=lambda state: state.score)
                else:
                    minValue = min([value, minValue], key=lambda state: state.score)
                beta = min(minValue.score, beta)
                if beta <= alpha:
                    break
            minValue.add_score(minValue.score + node.value)
            return minValue
