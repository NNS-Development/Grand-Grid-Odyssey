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

        self.boardwin = curses.newwin(self.rows-3, self.cols, 0, 0)
        self.msgwin = curses.newwin(2, self.cols-2, self.rows, 0)
        self.inputwin = curses.newwin(1, self.cols, self.rows, 0)

        self.msgwin.scrollok(True)

    def receive(self):
        '''receive user input'''

        prompt = "enter move (1-9): "

        while self.isuserturn:
            buf = ''
            try:
                self.inputwin.clear()
                self.inputwin.addstr(0, 0, prompt + buf)
                self.inputwin.refresh()

                key = self.inputwin.getch()

                match key:
                    case curses.KEY_ENTER | 10 | 13:
                        if buf.strip():
                            try:
                                buf = int(buf)-1
                                row, col = divmod(buf, 3)
                                if self.board[row][col] not in ["O", "X"]:
                                    self.board[row][col] = "O"
                                    yield buf
                                    buf = ''
                                    return buf
                                else:
                                    self.msgwin.addstr("⚠️ Field already occupied! Try again.")
                                    buf = ''
                                    continue
                            except (ValueError, IndexError):
                                self.msgwin.addstr(0, 0, "⚠️ Invalid input! Enter a number between 1 and 9.")
                                buf = ''
                                continue
                    case curses.KEY_BACKSPACE | 127:
                        buf = buf[:-1]
                    case _ if 0 <= key < 256:
                        buf += chr(key)
            except Exception as e:
                self.running = False

    def make_list_of_free_fields(self):
        return [(r, c) for r in range(3) for c in range(3) if self.board[r][c] not in ['O', 'X']]

    def victory_for(self, sgn):
        for row in self.board:
            if all(cell == sgn for cell in row):
                return True
        for col in range(3):
            if all(self.board[row][col] == sgn for row in range(3)):
                return True
        if all(self.board[i][i] == sgn for i in range(3)) or all(self.board[i][2 - i] == sgn for i in range(3)):
            return True
        return False

    def draw_move(self):
        free = self.make_list_of_free_fields()
        best_move = find_best_move(self.board, 'X') or find_best_move(self.board, 'O')
        if best_move:
            row, col = best_move
        else:
            row, col = choice(free)
        self.board[row][col] = 'X'
        displaytext = f"🤖 AI places 'X' at position {row*3+col+1}"
        self.msgwin.addstr(f"🤖 AI places 'X' at position {row*3+col+1}")

    def find_best_move(self, sgn):
        free = self.make_list_of_free_fields()
        for row, col in free:
            self.board[row][col] = sgn
            if self.victory_for(sgn):
                return row, col
            self.board[row][col] = str(3 * row + col + 1)  # Undo the move
        return None

    def display(self):
        '''displays the board'''
        self.stdscr.clear()
        self.stdscr.refresh()
        win = self.boardwin
        boardstate = ""

        boardstate += "+-------" * 3 + "+\n"
        for row in self.board:
            boardstate += "|       " * 3 + "|\n"
            boardstate += "|   " + "   |   ".join(row) + "   |\n"
            boardstate += "|       " * 3 + "|\n"
            boardstate += "+-------" * 3 + "+"

        win.addstr(0, 0, boardstate)

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
                    self.draw_move()
                    if victory_for(self.board, 'X'):
                        self.display()
                        print("🤖 I won! Better luck next time!")
                        break

                if not make_list_of_free_fields(self.board):
                    self.display()
                    print("😲 It's a tie! Well played!")
                    break

                self.isuserturn = not self.isuserturn

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
    except KeyboardInterrupt:
        pass
    except curses.error:
        pass

    print(error)
