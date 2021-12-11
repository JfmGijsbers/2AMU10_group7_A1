from team21_A1.helper_functions import check_legal_column, check_legal_region, check_legal_row

def evaluate_move(game_state, move, rmove, score): 

    count = 0 
    if check_legal_row(game_state.board, move.i, 0) == False:
        count +=1 
    if check_legal_column(game_state.board, move.j, 0) == False:
        count += 1      
    if check_legal_region(game_state.board, move.i, move.j, 0) == False:
        count += 1

    if count == 0:
        player_score = 0
    if count == 1:
        player_score = 1
    if count == 2:
        player_score = 3
    if count == 3:
        player_score = 7
    
    if rmove == True:
        return score + player_score
    else:
        return score - player_score