import curses
from random import choice

class TicTacToe():
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.running = True
        self.board = [[str(3 * j + i + 1) for i in range(3)] for j in range(3)]
        self.board[1][1] = 'X'
        self.isuserturn = True

        self.setupui()
        self.display()

    def setupui(self):
        '''initializes the window'''
        curses.curs_set(1)
        self.stdscr.nodelay(1)

        self.rows, self.cols = self.stdscr.getmaxyx()

        self.boardwin = curses.newwin(self.rows - 2, self.cols, 0, 0)
        self.msgwin = curses.newwin(2, self.cols, self.rows - 2, 0)
        self.inputwin = curses.newwin(1, self.cols, self.rows - 1, 0)
        self.msgwin.scrollok(True)

    def receive(self):
        '''receive user input'''
        prompt = "enter move (1-9): "
        buf = ''

        while self.isuserturn:
            try:
                self.inputwin.clear()
                self.inputwin.addstr(0, 0, prompt + buf)
                self.inputwin.refresh()

                key = self.inputwin.getch()

                match key:
                    case curses.KEY_ENTER | 10 | 13:
                        if buf.strip():
                            try:
                                move = int(buf) - 1
                                row, col = divmod(move, 3)
                                if self.board[row][col] not in ["O", "X"]:
                                    self.board[row][col] = "O"
                                    yield row, col
                                    buf = ''
                                    break
                                else:
                                    self.msgwin.addstr("⚠️ Field already occupied! Try again.\n")
                                    self.msgwin.refresh()
                                    continue
                            except (ValueError, IndexError):
                                self.msgwin.addstr("⚠️ Invalid input! Enter a number between 1 and 9.\n")
                                self.msgwin.refresh()
                                continue
                        buf = ''
                    case curses.KEY_BACKSPACE | 127:
                        buf = buf[:-1]
                    case _ if 0 <= key < 256:
                        buf += chr(key)
                    case _:
                        pass
            except Exception:
                self.running = False

    def getfreefields(self):
        return [(r, c) for r in range(3) for c in range(3) if self.board[r][c] not in ['O', 'X']]

    def isvictor(self, sgn):
        for row in self.board:
            if all(cell == sgn for cell in row):
                return True
        for col in range(3):
            if all(self.board[row][col] == sgn for row in range(3)):
                return True
        if all(self.board[i][i] == sgn for i in range(3)) or all(self.board[i][2 - i] == sgn for i in range(3)):
            return True
        return False

    def getbestmove(self, sgn):
        free = self.getfreefields()
        for row, col in free:
            self.board[row][col] = sgn
            if self.isvictor(sgn):
                return row, col
            self.board[row][col] = str(3 * row + col + 1)  # Undo the move

    def makemove(self):
        free = self.getfreefields()
        if not free:
            return
        if self.isuserturn:
            return
        free = self.getfreefields()
        best_move = self.getbestmove('X') or self.getbestmove('O')
        row, col = best_move if best_move else choice(free)
        self.board[row][col] = 'X'
        self.msgwin.addstr(f"🤖 AI places 'X' at position {row * 3 + col + 1}\n")
        self.msgwin.refresh()
        return

    def display(self):
        '''displays the board (also centers it :3)'''
        self.stdscr.clear()
        self.boardwin.clear()
        self.msgwin.clear()

        boardstate = "+-------" * 3 + "+\n"
        for row in self.board:
            boardstate += "|       " * 3 + "|\n"
            boardstate += "|   " + "   |   ".join(row) + "   |\n"
            boardstate += "|       " * 3 + "|\n"
            boardstate += "+-------" * 3 + "+\n"

        boardlines = boardstate.splitlines()
        boardh = len(boardlines)
        boardw = max(len(line) for line in boardlines)

        maxy, maxx = self.boardwin.getmaxyx()
        offsety = (maxy - boardh) // 2
        offsetx = (maxx - boardw) // 2

        for i, line in enumerate(boardlines):
            self.boardwin.addstr(offsety + i, offsetx, line)

        self.boardwin.refresh()
        self.msgwin.refresh()

    def run(self):
        '''main loop'''
        while True:
            self.display()
            if self.isuserturn:
                move = next(self.receive(), None)
                if move is not None:
                    if self.isvictor('O'):
                        self.display()
                        self.msgwin.addstr("🎉 You won! Congratulations!\n")
                        self.msgwin.refresh()
                        break
            else:
                self.makemove()
                if self.isvictor('X'):
                    self.display()
                    self.msgwin.addstr("🤖 I won! Better luck next time!\n")
                    self.msgwin.refresh()
                    break

            if not self.getfreefields():
                self.display()
                self.msgwin.addstr("😲 It's a tie! Well played!\n")
                self.msgwin.refresh()
                break
            self.isuserturn = not self.isuserturn

def main(stdscr):
    game = TicTacToe(stdscr)
    game.run()

    while game.running:
        try:
            curses.napms(500)
        except Exception as e:
            return e
    return "game over"


if __name__ == "__main__":
    error = ""
    try:
        error = curses.wrapper(main)
    except KeyboardInterrupt:
        pass
    except curses.error:
        pass

    print(error)
