import curses
from random import choice

class TicTacToe:
    def __init__(self, stdscr, side=3, mode="ai", human_first=True):
        self.side = side
        self.stdscr = stdscr
        self.mode = mode
        self.human_first = human_first
        self.running = True

        # initialize an empty board with cell numbers (as strings)
        self.board = [[str(self.side * j + i + 1) for i in range(self.side)] for j in range(self.side)]

        # Set tokens and starting turn depending on mode.
        if self.mode == "ai":
            if self.human_first:
                # Traditionally X goes first. So if you choose to start,
                # you'll be "X" and the AI will be "O".
                self.human_token = "X"
                self.ai_token = "O"
                self.current_turn = "human"
            else:
                self.human_token = "O"
                self.ai_token = "X"
                self.current_turn = "ai"
        elif self.mode == "2p":
            # In two-player mode, Player 1 is X and goes first.
            self.player1_token = "X"
            self.player2_token = "O"
            self.current_turn = "player1"

        # Initialize colors for better UI
        if curses.has_colors():
            curses.start_color()
            curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)    # X
            curses.init_pair(2, curses.COLOR_BLUE, curses.COLOR_BLACK)   # O
            curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_BLACK)  # numbers/others

        self.setupui()
        self.display()

    def setupui(self):
        """Initializes the window."""
        curses.curs_set(1)
        self.stdscr.nodelay(1)
        self.rows, self.cols = self.stdscr.getmaxyx()

        # Create windows for board, messages, and input.
        self.boardwin = curses.newwin(self.rows - 2, self.cols, 0, 0)
        self.msgwin = curses.newwin(2, self.cols, self.rows - 2, 0)
        self.inputwin = curses.newwin(1, self.cols, self.rows - 1, 0)
        self.msgwin.scrollok(True)
        self.inputwin.nodelay(True)

    def get_move(self, prompt):
        """Receives a move from the user.
        Returns (row, col) if a valid move (number 1-9) is entered."""
        buf = ""
        # Set input to blocking mode while waiting for a move.
        self.inputwin.nodelay(False)
        while True:
            self.inputwin.clear()
            self.inputwin.addstr(0, 0, prompt + buf)
            self.inputwin.refresh()
            key = self.inputwin.getch()

            if key in [curses.KEY_ENTER, 10, 13]:
                if buf.strip():
                    try:
                        move = int(buf.strip())
                        if move < 1 or move > 9:
                            self.msgwin.addstr("⚠️ Invalid input! Enter a number between 1 and 9.\n")
                            self.msgwin.refresh()
                            buf = ""
                            continue
                        row, col = divmod(move - 1, 3)
                        if self.board[row][col] in ["X", "O"]:
                            self.msgwin.addstr("⚠️ Field already occupied! Try again.\n")
                            self.msgwin.refresh()
                            buf = ""
                            continue
                        else:
                            self.inputwin.nodelay(True)
                            return row, col
                    except ValueError:
                        self.msgwin.addstr("⚠️ Invalid input! Enter a number between 1 and 9.\n")
                        self.msgwin.refresh()
                        buf = ""
                        continue
            elif key in [curses.KEY_BACKSPACE, 127]:
                buf = buf[:-1]
            elif 0 <= key < 256:
                buf += chr(key)
            # Ignore any other keys

    def getfreefields(self):
        return [(r, c) for r in range(3) for c in range(3) if self.board[r][c] not in ['X', 'O']]

    def isvictor(self, sgn):
        # Check rows and columns.
        for row in self.board:
            if all(cell == sgn for cell in row):
                return True
        for col in range(3):
            if all(self.board[row][col] == sgn for row in range(3)):
                return True
        # Check diagonals.
        if all(self.board[i][i] == sgn for i in range(3)) or all(self.board[i][2 - i] == sgn for i in range(3)):
            return True
        return False

    def getbestmove(self, sgn):
        """For AI: Try each free cell; if placing sgn there wins the game, return that move."""
        free = self.getfreefields()
        for row, col in free:
            # Temporarily place sgn
            orig = self.board[row][col]
            self.board[row][col] = sgn
            if self.isvictor(sgn):
                self.board[row][col] = orig  # Undo the move
                return row, col
            self.board[row][col] = orig  # Undo the move

    def makemove(self):
        """AI move: first try to win, then block opponent, else pick random."""
        free = self.getfreefields()
        if not free:
            return ""
        best_move = self.getbestmove(self.ai_token)
        if not best_move:
            best_move = self.getbestmove(self.human_token)
        if not best_move:
            best_move = choice(free)
        row, col = best_move
        self.board[row][col] = self.ai_token
        return f"🤖 AI places '{self.ai_token}' at position {row * 3 + col + 1}\n"

    def display(self):
        """Displays the board (centered on the screen)."""
        self.stdscr.clear()
        self.boardwin.clear()

        # Calculate board dimensions.
        boardh = self.side * 3 + self.side + 1
        boardw = self.side * 7 + self.side + 1
        maxy, maxx = self.boardwin.getmaxyx()
        offsety = (maxy - boardh) // 2
        offsetx = (maxx - boardw) // 2

        # Draw horizontal lines.
        for i in range(self.side + 1):
            y = offsety + i * 4
            self.boardwin.hline(y, offsetx, curses.ACS_HLINE, boardw)
        # Draw vertical lines.
        for i in range(self.side + 1):
            x = offsetx + i * 8
            self.boardwin.vline(offsety, x, curses.ACS_VLINE, boardh)
        # Draw intersections.
        for i in range(self.side + 1):
            for j in range(self.side + 1):
                y = offsety + i * 4
                x = offsetx + j * 8
                self.boardwin.addch(y, x, curses.ACS_PLUS)

        # Insert tokens/numbers into the cells.
        for r in range(self.side):
            for c in range(self.side):
                token = self.board[r][c]
                celly = offsety + r * 4 + 2
                cellx = offsetx + c * 8 + 4
                if token == 'X':
                    attr = curses.color_pair(1) | curses.A_BOLD
                elif token == 'O':
                    attr = curses.color_pair(2) | curses.A_BOLD
                else:
                    attr = curses.color_pair(3)
                self.boardwin.addstr(celly, cellx, token, attr)

        self.boardwin.refresh()
        self.msgwin.refresh()

    def run(self):
        """Main game loop."""
        while True:
            self.display()
    
            if self.mode == "ai":
                if self.current_turn == "human":
                    prompt = f"Your move ({self.human_token}), enter move (1-9): "
                    row, col = self.get_move(prompt)
                    self.board[row][col] = self.human_token
                    if self.isvictor(self.human_token):
                        self.display()
                        self.msgwin.addstr("🎉 You won! Congratulations!\n")
                        self.msgwin.refresh()
                        return self.human_token
                    self.current_turn = "ai"
                else:  # AI turn
                    msg = self.makemove()
                    if msg:
                        self.msgwin.addstr(msg)
                        self.msgwin.refresh()
                    if self.isvictor(self.ai_token):
                        self.display()
                        self.msgwin.addstr("🤖 I won! Better luck next time!\n")
                        self.msgwin.refresh()
                        return self.ai_token
                    self.current_turn = "human"
            elif self.mode == "2p":
                if self.current_turn == "player1":
                    prompt = "Player 1 (X), enter move (1-9): "
                    row, col = self.get_move(prompt)
                    self.board[row][col] = self.player1_token
                    if self.isvictor(self.player1_token):
                        self.display()
                        self.msgwin.addstr("🎉 Player 1 (X) won! Congratulations!\n")
                        self.msgwin.refresh()
                        return "X"
                    self.current_turn = "player2"
                else:
                    prompt = "Player 2 (O), enter move (1-9): "
                    row, col = self.get_move(prompt)
                    self.board[row][col] = self.player2_token
                    if self.isvictor(self.player2_token):
                        self.display()
                        self.msgwin.addstr("🎉 Player 2 (O) won! Congratulations!\n")
                        self.msgwin.refresh()
                        return "O"
                    self.current_turn = "player1"
    
            if not self.getfreefields():
                self.display()
                self.msgwin.addstr("😲 It's a tie! Well played!\n")
                self.msgwin.refresh()
                return "tie"

def main_menu(stdscr):
    """Display the main menu and return chosen mode and settings."""
    stdscr.clear()
    stdscr.addstr("Welcome to Tic Tac Toe!\n\n")
    stdscr.addstr("Choose game mode:\n")
    stdscr.addstr("  1. Play against AI\n")
    stdscr.addstr("  2. Two Player mode\n")
    stdscr.addstr("\nPress 1 or 2 to choose.\n")
    stdscr.refresh()
    while True:
        key = stdscr.getch()
        if key in [ord('1'), ord('2')]:
            mode = "ai" if key == ord('1') else "2p"
            break

    human_first = True
    if mode == "ai":
        stdscr.clear()
        stdscr.addstr("Do you want to start first? (y/n): ")
        stdscr.refresh()
        while True:
            key = stdscr.getch()
            if key in [ord('y'), ord('Y')]:
                human_first = True
                break
            elif key in [ord('n'), ord('N')]:
                human_first = False
                break
    return mode, human_first

def main(stdscr):
    curses.curs_set(0)  # hide cursor in menus
    while True:
        mode, human_first = main_menu(stdscr)
        # Inner loop: play the game repeatedly in the same mode.
        while True:
            game = TicTacToe(stdscr, mode=mode, human_first=human_first)
            winner = game.run()  # Modify run() to return the winner

            # After game ends, show restart/menu prompt with winner info
            stdscr.nodelay(False)
            stdscr.clear()
            if mode == "2p" and winner in ["X", "O"]:
                stdscr.addstr(f"Game over! Player {winner} wins!\n")
            else:
                stdscr.addstr("Game over!\n")
            stdscr.addstr("Press 'r' to restart, 'm' for main menu, or 'q' to quit.\n")
            stdscr.refresh()
            key = stdscr.getch()
            if key in [ord('r'), ord('R')]:
                continue  # restart with the same settings
            elif key in [ord('m'), ord('M')]:
                break  # go back to main menu
            elif key in [ord('q'), ord('Q')]:
                return
                
if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        pass
    except curses.error:
        pass
