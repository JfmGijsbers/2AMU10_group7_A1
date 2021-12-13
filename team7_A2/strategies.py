def single_possibility(selfself, game_state: GameState) -> List[Move]:
    N = game_state.board.N
    m = game_state.board.m
    n = game_state.board.n

    def calc_sq(i,j):
        pass
    all_moves = []
    row_set[i] = {val for val in range(1, N + 1)}
    col_set[j] = {val for val in range(1, N + 1)}
    sq_set[calc_sq(i,j)] = {val for val in range(1, N + 1)}

    for i in range(N):
        for j in range(N):
            if game_state.board.get(i, j) != SudokuBoard.empty:
                row_set[i].remove(gate_state.board.get(i, j))
                row_set[j].remove(gate_state.board.get(i, j))
                sq_set[calc_sq(i, j)].remove(gate_state.board.get(i,j))
            else:
                pos_moves.append((i,j))

    for pos_move in pos_moves:
        i_row = pos_move[0]
        i_col = col_move[1]
        i_sq = calc_sq(i_row, i_col)
        pos_vals = intersection(row_set[i_row], col_set[i_col], sq_set[i_sq])
        for pos_val in pos_vals:
            if not TabooMove(i, j, pos_val) in game_state.taboo_moves:
                all_moves.append(Move(i_row, i_col, pos_val))

    return all_moves