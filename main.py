from random import choice

def display_board(board):
    print("\n   Tic-Tac-Toe Arena")
    print("+-------" * 3, "+", sep="")
    for row in board:
        print("|       " * 3, "|", sep="")
        print("|   " + "   |   ".join(row) + "   |")
        print("|       " * 3, "|", sep="")
        print("+-------" * 3, "+", sep="")

def make_list_of_free_fields(board):
    return [(r, c) for r in range(3) for c in range(3) if board[r][c] not in ['O', 'X']]

def victory_for(board, sgn):
    for row in board:
        if all(cell == sgn for cell in row):
            return True
    for col in range(3):
        if all(board[row][col] == sgn for row in range(3)):
            return True
    if all(board[i][i] == sgn for i in range(3)) or all(board[i][2 - i] == sgn for i in range(3)):
        return True
    return False

def enter_move(board):
    while True:
        try:
            move = int(input("Enter your move (1-9): ")) - 1
            row, col = divmod(move, 3)
            if board[row][col] not in ['O', 'X']:
                board[row][col] = 'O'
                return
            else:
                print("⚠️ Field already occupied! Try again.")
        except (ValueError, IndexError):
            print("⚠️ Invalid input! Enter a number between 1 and 9.")

def find_best_move(board, sgn):
    free = make_list_of_free_fields(board)
    for row, col in free:
        board[row][col] = sgn
        if victory_for(board, sgn):
            return row, col
        board[row][col] = str(3 * row + col + 1)  # Undo the move
    return None

def draw_move(board):
    free = make_list_of_free_fields(board)
    best_move = find_best_move(board, 'X') or find_best_move(board, 'O')
    if best_move:
        row, col = best_move
    else:
        row, col = choice(free)
    board[row][col] = 'X'
    print("🤖 AI places 'X' at position", row * 3 + col + 1)

def tic_tac_toe():
    while True:
        board = [[str(3 * j + i + 1) for i in range(3)] for j in range(3)]
        board[1][1] = 'X'
        human_turn = True
        
        while True:
            display_board(board)
            if human_turn:
                enter_move(board)
                if victory_for(board, 'O'):
                    display_board(board)
                    print("🎉 You won! Congratulations!")
                    break
            else:
                draw_move(board)
                if victory_for(board, 'X'):
                    display_board(board)
                    print("🤖 I won! Better luck next time!")
                    break
            
            if not make_list_of_free_fields(board):
                display_board(board)
                print("😲 It's a tie! Well played!")
                break
            
            human_turn = not human_turn
        
        if input("🔄 Play again? (y/n): ").lower() != 'y':
            print("👋 Thanks for playing! See you next time!")
            break

tic_tac_toe()
