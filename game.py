from checkers import Bitboard, count_bits
from ai import AI
import time

class Game:
    def __init__(self):
        self.side_names = ['BLACK', 'WHITE']

    def new_game(self):
        modes = ['Player vs Player', 'Player vs Computer', 'Computer vs Computer']
        mode = self.prompt('Welcome to checkers! Enter a number to continue.', modes)
        if mode > 0:
            timelimit = self.prompt('Enter a time limit (<=20s) for the AI:')
            self.ai = AI(timelimit)
        if mode == 1:
            side = self.prompt('Select a side:', self.side_names)

        blank = Bitboard((0, 0, 0, 0))
        if self.prompt('Would you like to specify a starting board?', ['No', 'Yes']):
            blank.print_board()
            black = self.prompt_list('Specify whitespace delimited list of black pieces: ')
            white = self.prompt_list('Specify whitespace delimited list of white pieces: ')
            kings = self.prompt_list('Specify whitespace delimited list of kings: ')
            side = self.prompt('Specify starting side: ', ['BLACK', 'WHITE'])
            twokings = (2**0, 2**9 + 2**13, 2**0 + 2**9 + 2**13, 1)
            draw = (2**12, 2**21, 2**12 + 2**21, 1)
            self.board = Bitboard((black, white, kings & (white | black), side))
        else:
            self.board = Bitboard()

        check_draws = self.prompt('Enable draw detection (experimental): ', ['No', 'Yes'])

        print('New game starting...')

        while (len(self.board.get_moves()) > 0):
            self.board.print_board()

            if mode == 0:
                self.player_move()
            elif mode == 1:
                if side == self.board.side:
                    self.player_move()
                else:
                    self.ai_move()
            elif mode == 2:
                self.ai_move()
            
            # Considered a draw if each side has one king and there is no jump
            if check_draws and self.is_draw():
                self.board.print_board()
                return self.prompt('Game ended in a draw.', ['Play again', 'Quit'])
        self.board.print_board()
        return self.prompt('{} wins.'.format(self.side_names[~self.board.side]),
                ['Play again', 'Quit'])

    def player_move(self):
        moves = self.board.get_moves()
        i = self.prompt('{}\'s turn, select a move'.format(self.side_names[self.board.side]),
                [self.board.format_move(m) for m in moves])
        self.board.make_move(moves[i])

    def ai_move(self):
        print('Finding best move for {}...'.format(self.side_names[self.board.side]))
        start = time.time()
        move = self.ai.iddfs(self.board)
        elapsed = time.time() - start
        print('  {} selected move {} in {:.3f}s'.format(self.side_names[self.board.side], self.board.format_move(move), elapsed))
        self.board.make_move(move)
    
    def is_draw(self):
        stuck = False
        if self.board.side == self.board.BLACK:
            stuck = self.board.black & ~0x00181800
        else:
            stuck = self.board.white & ~0x00181800

        return (count_bits(self.board.black) == 1 and 
                count_bits(self.board.white) == 1 and 
                self.board.black & self.board.kings and
                self.board.white & self.board.kings and
                len(self.board.get_moves()) > 1 and
                stuck)

    def get_custom_board(self):
        self.prompt()
    
    def prompt_list(self, message):
         while True:
            try:
                text = input(message).split()
                spaces = []
                for item in text:
                    if 0 <= int(item) < 32:
                        spaces.append(int(item))
                    else:
                        raise ValueError
                return sum([2**space for space in spaces])
            except ValueError:
                continue


    def prompt(self, message, options=[]):
        while True:
            try:
                selection = int(input(message + '\n'
                + ''.join(['  {!s:>2}.) {}\n'.format(i, o) for i, o in enumerate(options)])
                + '--> '))
            except ValueError:
                continue
            if not options:
                if selection <= 20:
                    return selection
                else:
                    continue
            elif 0 <= selection < len(options):
                return selection
            else:
                continue

game = Game()
while True:
    retval = game.new_game()
    if retval:
        break

