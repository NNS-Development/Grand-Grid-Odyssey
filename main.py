from tomlkit.api import E
import curses
from random import choice

class TicTacToe():
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.running = True
        self.board = [[str(3 * j + i + 1) for i in range(3)] for j in range(3)]
        self.isuserturn = False

        self.setupui()
        self.display()


    def setupui(self):
        '''initializes the window'''
        curses.curs_set(1)
        self.stdscr.nodelay(1)

        self.rows, self.cols = self.stdscr.getmaxyx()

        self.boardwin = curses.newwin(self.rows-1, self.cols, 0, 0)
        self.inputwin = curses.newwin(1, self.cols, self.rows, 0)

    def receive(self):
        '''receive user input (messages)'''

        buf = ''
        prompt = "> "

        while self.isuserturn:
            try:
                self.inputwin.clear()
                self.inputwin.addstr(0, 0, prompt + buf)
                self.inputwin.refresh()

                key = self.inputwin.getch()

                match key:
                    case curses.KEY_ENTER | 10 | 13:
                        if buf.strip():
                            # TODO: handle user input
                            pass
                    case curses.KEY_BACKSPACE | 127:
                        buf = buf[:-1]
                    case _ if 0 <= key < 256:
                        buf += chr(key)
            except Exception as e:
                self.running = False

    def display(self):
        '''displays the board'''
        self.stdscr.clear()
        self.stdscr.refresh()
        win = self.boardwin

        win.addstr(0, 0, "+-------" * 3, "+", sep="")
        for row in self.board:
            win.addstr(0, 0, "|       " * 3, "|", sep="")
            win.addstr(0, 0, "|   " + "   |   ".join(row) + "   |")
            win.addstr(0, 0, "|       " * 3, "|", sep="")
        win.addstr(0, 0, "+-------" * 3, "+", sep="")

    def run(self):
        '''main loop'''
        while True:
            self.board[1][1] = 'X'
            self.isuserturn = True

            while True:
                self.display()
                if self.isuserturn:
                    enter_move(self.board)
                    if victory_for(self.board, 'O'):
                        self.display()
                        print("🎉 You won! Congratulations!")
                        break
                else:
                    draw_move()
                    if victory_for(self.board, 'X'):
                        self.display()
                        print("🤖 I won! Better luck next time!")
                        break

                if not make_list_of_free_fields(self.board):
                    self.display()
                    print("😲 It's a tie! Well played!")
                    break

                self.isuserturn = not self.isuserturn

            if input("🔄 Play again? (y/n): ").lower() != 'y':
                print("👋 Thanks for playing! See you next time!")
                break

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

def main(stdscr):
    '''main loop'''
    game = TicTacToe(stdscr)
    game.run()

    while game.running:
        try:
            curses.napms(500) # instead of time.sleep because sigma
        except Exception as e:
            return e
        return "game ended"


if __name__ == "__main__":
    error = ""
    try:
        error = curses.wrapper(main)
    except XeyboardInterrupt:
        pass
    except curses.error:
        pass

    print(error)
