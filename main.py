import curses
import json
import os
import time
from typing import Dict, List, Any, Optional, Tuple
from random import choice

STREAK_FILE = "streak.json"
Board = List[List[str]]

def load_streak() -> Dict[str, int]:
    '''loads the win/loss streak from file'''
    data: Dict[str, int] = {"win_streak": 0, "loss_streak": 0}
    if os.path.exists(STREAK_FILE):
        with open(STREAK_FILE, "r") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                pass
    return data

def save_streak(streak) -> None:
    '''saves the win/loss streak to file'''
    with open(STREAK_FILE, "w") as f:
        json.dump(streak, f)

class TicTacToe:
    def __init__(self, stdscr: Any, side: int = 3, mode: str = "ai", human_first: bool = True, timed_mode: bool = False, turn_time: int = 10) -> None:
        self.side: int = side
        self.stdscr: Any = stdscr
        self.mode: str = mode
        self.human_first: bool = human_first
        self.timed_mode: bool= timed_mode      # Enable timed mode?
        self.turn_time: int = turn_time        # Seconds per turn
        self.running: bool = True

        # Initialize board with cell numbers
        self.board: Board = [
            [str(self.side * j + i + 1) for i in range(self.side)] 
            for j in range(self.side)
        ]

        # Set tokens and starting turn
        self.current_turn: str = "ai"
        if self.mode == "ai":
            self.human_token: str = "O"
            self.ai_token: str = "X"
            if self.human_first:
                self.human_token = "X"
                self.ai_token = "O"
                self.current_turn = "human"
        elif self.mode == "2p":
            self.player1_token: str = "X"
            self.player2_token: str = "O"
            self.current_turn = "player1"

        # Initialize colors if available
        if curses.has_colors():
            curses.start_color()
            curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)    # For X
            curses.init_pair(2, curses.COLOR_BLUE, curses.COLOR_BLACK)   # For O
            curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_BLACK)  # For numbers/others

        self.setupui()
        self.display()

    def setupui(self) -> None:
        curses.curs_set(1)
        self.stdscr.nodelay(1)
        rowcol: Tuple[int, int] = self.stdscr.getmaxyx()
        self.rows: int = rowcol[0]
        self.cols: int = rowcol[1]
        self.boardwin: curses.window = curses.newwin(self.rows - 2, self.cols, 0, 0)
        self.msgwin: curses.window = curses.newwin(2, self.cols, self.rows - 2, 0)
        self.inputwin: curses.window = curses.newwin(1, self.cols, self.rows - 1, 0)
        self.msgwin.scrollok(True)
        self.inputwin.nodelay(True)

    def __get_move_normal(self, prompt: str) -> Tuple[int, int]:
        '''gets user input for move'''
        buf: str = "" # buffer to store user input
        self.inputwin.nodelay(False)
        while True:
            # displays the prompt and what the user already inputs every cycle
            self.inputwin.clear()
            self.inputwin.addstr(0, 0, prompt + buf)
            self.inputwin.refresh()

            key: int = self.inputwin.getch() # whatever key the user inputs
            if key in [curses.KEY_ENTER, 10, 13]: # if user presses enter
                if not buf.strip():
                    continue
                try:
                    move: int = int(buf.strip())
                    if move < 1 or move > 9:
                        self.msgwin.addstr("⚠️ Invalid input! Enter a number between 1 and 9.\n")
                        self.msgwin.refresh()
                        buf = ""
                        continue
                    # funny math thing to get the row and column from the move
                    rowcol: Tuple[int, int] = divmod(move - 1, 3)
                    row: int = rowcol[0]
                    col: int = rowcol[1]
                    if self.board[row][col] in ["X", "O"]:
                        self.msgwin.addstr("⚠️ Field already occupied! Try again.\n")
                        self.msgwin.refresh()
                        buf = ""
                        continue
                    return row, col
                except ValueError:
                    self.msgwin.addstr("⚠️ Invalid input! Enter a number between 1 and 9.\n")
                    self.msgwin.refresh()
                    buf = ""
                    continue
            elif key in [curses.KEY_BACKSPACE, 127]: # if user presses backspace
                buf = buf[:-1]
            elif 0 <= key < 256: # any other key
                buf += chr(key)

    def __get_move_timed(self, prompt: str) -> Optional[Tuple[int, int]]:
        '''same as get_move_normal but with a timer'''
        # vars init
        buf: str = ""
        start_time: float = time.time()
        total_time: int = self.turn_time
        elapsed: float = 0.0
        remaining: int = 0
        self.inputwin.nodelay(True)

        while True:
            elapsed = time.time() - start_time
            remaining = int(total_time - elapsed)
            if remaining <= 0:
                self.msgwin.clear()
                self.msgwin.addstr("⏰ Time's up! You lose by timeout!\n")
                self.msgwin.refresh()
                return None
            self.inputwin.clear()
            self.inputwin.addstr(0, 0, f"{prompt} (Time remaining: {remaining} sec): " + buf)
            self.inputwin.refresh()
            key: int = self.inputwin.getch()
            if key != -1:
                if key in [curses.KEY_ENTER, 10, 13]:
                    if not buf.strip():
                        continue
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
            time.sleep(0.1)

    def get_move(self, prompt: str) -> Optional[Tuple[int, int]]:
        '''wrapper function for get_move_normal and get_move_timed'''
        if self.timed_mode:
            return self.__get_move_timed(prompt)
        return self.__get_move_normal(prompt)

    def getfreefields(self) -> List[Tuple[int, int]]:
        '''returns a list of free fields on the board'''
        return [(r, c) for r in range(3) for c in range(3) if self.board[r][c] not in ['X', 'O']]

    def isvictor(self, sgn: str) -> bool:
        '''check if player with token sgn has won'''
        for row in self.board:
            if all(cell == sgn for cell in row):
                return True
        for col in range(3):
            if all(self.board[row][col] == sgn for row in range(3)):
                return True
            
        if all(self.board[i][i] == sgn for i in range(3)) or all(self.board[i][2 - i] == sgn for i in range(3)):
            return True
        return False

    def getbestmove(self, sgn: str) -> Optional[Tuple[int, int]]:
        '''ai's algorithm'''
        free = self.getfreefields()
        for row, col in free:
            orig: str = self.board[row][col]
            self.board[row][col] = sgn
            if self.isvictor(sgn):
                self.board[row][col] = orig
                return row, col
            self.board[row][col] = orig
        return None

    def makemove(self) -> str:
        free: List[Tuple[int, int]] = self.getfreefields()
        if not free:
            return ""
        best_move: Optional[Tuple[int, int]] = self.getbestmove(self.ai_token)
        if not best_move:
            best_move = self.getbestmove(self.human_token)
        if not best_move:
            best_move = choice(free)
        
        row: int = best_move[0]
        col: int = best_move[1]
        self.board[row][col] = self.ai_token

        return f"🤖 AI places '{self.ai_token}' at position {row * 3 + col + 1}\n"

    def display(self) -> None:
        self.stdscr.clear()
        self.boardwin.clear()

        # var init
        boardh: int = self.side * 3 + self.side + 1
        boardw: int = self.side * 7 + self.side + 1
        maxes: Tuple[int, int] = self.boardwin.getmaxyx()
        maxy: int = maxes[0]
        maxx: int = maxes[1]
        offsety: int = (maxy - boardh) // 2
        offsetx: int = (maxx - boardw) // 2
        y: int = 0
        x: int = 0
        celly: int = 0
        cellx: int = 0

        for i in range(self.side + 1):
            y = offsety + i * 4
            self.boardwin.hline(y, offsetx, curses.ACS_HLINE, boardw)
        for i in range(self.side + 1):
            x = offsetx + i * 8
            self.boardwin.vline(offsety, x, curses.ACS_VLINE, boardh)
        for i in range(self.side + 1):
            for j in range(self.side + 1):
                y = offsety + i * 4
                x = offsetx + j * 8
                self.boardwin.addch(y, x, curses.ACS_PLUS)
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

    def run(self) -> str:
        while True:
            self.display()
            if self.mode == "ai":
                if self.current_turn == "human":
                    prompt: str = f"Your move ({self.human_token}), enter move (1-9): "
                    move: Optional[Tuple[int, int]] = self.get_move(prompt)
                    if move is None:
                        self.display()
                        self.msgwin.addstr("⏰ Time's up! You lose by timeout!\n")
                        self.msgwin.refresh()
                        return self.ai_token
                    row: int = move[0]
                    col: int = move[1]
                    self.board[row][col] = self.human_token
                    if self.isvictor(self.human_token):
                        self.display()
                        self.msgwin.addstr("🎉 You won! Congratulations!\n")
                        self.msgwin.refresh()
                        return self.human_token
                    self.current_turn = "ai"
                else:
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
                    move = self.get_move(prompt)
                    if move is None:
                        self.display()
                        self.msgwin.addstr("⏰ Time's up! Player 1 loses by timeout!\n")
                        self.msgwin.refresh()
                        return "O"  # Player2 wins
                    row, col = move
                    self.board[row][col] = self.player1_token
                    if self.isvictor(self.player1_token):
                        self.display()
                        self.msgwin.addstr("🎉 Player 1 (X) won! Congratulations!\n")
                        self.msgwin.refresh()
                        return "X"
                    self.current_turn = "player2"
                else:
                    prompt = "Player 2 (O), enter move (1-9): "
                    move = self.get_move(prompt)
                    if move is None:
                        self.display()
                        self.msgwin.addstr("⏰ Time's up! Player 2 loses by timeout!\n")
                        self.msgwin.refresh()
                        return "X"  # Player1 wins
                    row, col = move
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
    timed_mode = False
    stdscr.clear()
    stdscr.addstr("Enable Timed Mode? (Each turn has a countdown timer) (y/n): ")
    stdscr.refresh()
    while True:
        key = stdscr.getch()
        if key in [ord('y'), ord('Y')]:
            timed_mode = True
            break
        elif key in [ord('n'), ord('N')]:
            timed_mode = False
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
    return mode, human_first, timed_mode

def main(stdscr):
    curses.curs_set(0)  # Hide cursor in menus
    streak = load_streak()
    while True:
        mode, human_first, timed_mode = main_menu(stdscr)
        while True:
            game = TicTacToe(stdscr, mode=mode, human_first=human_first, timed_mode=timed_mode)
            winner = game.run()
            stdscr.nodelay(False)
            stdscr.clear()
            if mode == "2p" and winner in ["X", "O"]:
                stdscr.addstr(f"Game over! Player {winner} wins!\n")
            else:
                stdscr.addstr("Game over!\n")
            if mode == "ai":
                if winner == game.human_token:
                    streak["win_streak"] += 1
                    streak["loss_streak"] = 0
                    result_msg = f"🤩 You won! Current win streak: {streak['win_streak']}"
                elif winner == game.ai_token:
                    streak["loss_streak"] += 1
                    streak["win_streak"] = 0
                    result_msg = f"😞 AI won! Current loss streak: {streak['loss_streak']}"
                else:
                    streak["win_streak"] = 0
                    streak["loss_streak"] = 0
                    result_msg = "😐 It's a tie! Streak reset."
                save_streak(streak)
                stdscr.addstr(result_msg + "\n")
            stdscr.addstr("Press 'r' to restart, 'm' for main menu, or 'q' to quit.\n")
            stdscr.refresh()
            key = stdscr.getch()
            if key in [ord('r'), ord('R')]:
                continue
            elif key in [ord('m'), ord('M')]:
                break
            elif key in [ord('q'), ord('Q')]:
                return

if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        pass
    except curses.error:
        pass
