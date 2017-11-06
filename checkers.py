import numpy as np
from termcolor import colored, cprint

class Bitboard:
    # All even row squares can move to the left and all odd row squares
    #   can move to the right with a bitshift of 4. The following masks define
    #   squares from which pieces can perform bitshifts of 3 and 5.

    # Even rows: 0x07 -> 0b00000111
    MASK_SE = 0x07070707 # southeast
    MASK_NE = 0x07070700 # northeast

    # Odd rows: 0xe0 -> 0b11100000
    MASK_SW = 0x00e0e0e0 # southwest
    MASK_NW = 0xe0e0e0e0 # northwest

    BLACK, WHITE = 0, 1

    def __init__(self, preset=None):
        if preset:
            self.black = np.uint32(preset['black'])
            self.white = np.uint32(preset['white'])
            self.kings = np.uint32(preset['kings'])
            self.side = preset['side']
        else:
            self.black = np.uint32(2**12-1)
            self.white = np.uint32(2**32 - 2**20)
            self.kings = np.uint32(0)
            self.side = self.BLACK

    def get_moves(self):
        # Construct list of moves, where each move is a bitboard
        #   containing the current location and the moved location.
        #   ex. 0x11 = 10001, a piece at 1 and a piece at 1 << 4.

        jumps = self.get_jumps()
        if jumps:
            return jumps

        empty_squares = np.uint32(~(self.black | self.white))
        moves = []
        if self.side == self.BLACK:
            movable = (empty_squares >> 4) & self.black
            moves += [0x11 << bit for bit, piece in enumerate(bin(movable)[:1:-1]) if piece == '1']
            movable = (empty_squares >> 3) & self.black & self.MASK_SW
            moves += [0x09 << bit for bit, piece in enumerate(bin(movable)[:1:-1]) if piece == '1']
            movable = (empty_squares >> 5) & self.black & self.MASK_SE
            moves += [0x21 << bit for bit, piece in enumerate(bin(movable)[:1:-1]) if piece == '1']

            movable = (empty_squares << 4) & self.black & self.kings
            moves += [0x11 << bit-4 for bit, piece in enumerate(bin(movable)[:1:-1]) if piece == '1']
            movable = (empty_squares << 3) & self.black & self.kings & self.MASK_NE
            moves += [0x09 << bit-3 for bit, piece in enumerate(bin(movable)[:1:-1]) if piece == '1']
            movable = (empty_squares << 5) & self.black & self.kings & self.MASK_NW
            moves += [0x21 << bit-5 for bit, piece in enumerate(bin(movable)[:1:-1]) if piece == '1']

            return moves;

        else:
            movable = (empty_squares << 4) & self.white
            moves += [0x11 << bit-4 for bit, piece in enumerate(bin(movable)[:1:-1]) if piece == '1']
            movable = (empty_squares << 3) & self.white & self.MASK_NE
            moves += [0x09 << bit-3 for bit, piece in enumerate(bin(movable)[:1:-1]) if piece == '1']
            movable = (empty_squares << 5) & self.white & self.MASK_NW
            moves += [0x21 << bit-5 for bit, piece in enumerate(bin(movable)[:1:-1]) if piece == '1']

            movable = (empty_squares >> 4) & self.white & self.kings
            moves += [0x11 << bit for bit, piece in enumerate(bin(movable)[:1:-1]) if piece == '1']
            movable = (empty_squares >> 3) & self.white & self.kings & self.MASK_SW
            moves += [0x09 << bit for bit, piece in enumerate(bin(movable)[:1:-1]) if piece == '1']
            movable = (empty_squares >> 5) & self.white & self.kings & self.MASK_SE
            moves += [0x21 << bit for bit, piece in enumerate(bin(movable)[:1:-1]) if piece == '1']

            return moves;

    def get_jumps(self):
        empty_squares = np.uint32(~(self.black | self.white))
        jumps = []
        if self.side == self.BLACK:
            kings = self.black & self.kings

            takeable = (empty_squares >> 4) & self.white
            if takeable:
                movable = (takeable >> 3) & self.black & self.MASK_SW
                jumps += [0x89 << bit for bit, piece in enumerate(bin(movable)[:1:-1]) if piece == '1']
                movable = (takeable >> 5) & self.black & self.MASK_SE
                jumps += [0x221 << bit for bit, piece in enumerate(bin(movable)[:1:-1]) if piece == '1']

            takeable = (empty_squares >> 3) & self.white & self.MASK_SW
            if takeable:
                movable = (takeable >> 4) & self.black
                jumps += [0x91 << bit for bit, piece in enumerate(bin(movable)[:1:-1]) if piece == '1']

            takeable = (empty_squares >> 5) & self.white & self.MASK_SE
            if takeable:
                movable = (takeable >> 4) & self.black
                jumps += [0x211 << bit for bit, piece in enumerate(bin(movable)[:1:-1]) if piece == '1']

            takeable = (empty_squares << 4) & self.white
            if takeable:
                movable = (takeable << 3) & kings & self.MASK_NE
                jumps += [0x91 << bit-7 for bit, piece in enumerate(bin(movable)[:1:-1]) if piece == '1']
                movable = (takeable << 5) & kings & self.MASK_NW
                jumps += [0x211 << bit-9 for bit, piece in enumerate(bin(movable)[:1:-1]) if piece == '1']

            takeable = (empty_squares << 3) & self.white & self.MASK_NE
            if takeable:
                movable = (takeable << 4) & kings
                jumps += [0x89 << bit-7 for bit, piece in enumerate(bin(movable)[:1:-1]) if piece == '1']

            takeable = (empty_squares << 5) & self.white & self.MASK_NW
            if takeable:
                movable = (takeable << 4) & kings
                jumps += [0x221 << bit-9 for bit, piece in enumerate(bin(movable)[:1:-1]) if piece == '1']

            complete_jumps = set()
            for jump in jumps:
                complete_jumps.update(self.jump_from(jump))
            return list(complete_jumps)

        else:
            takeable = (empty_squares << 4) & self.black
            if takeable:
                movable = (takeable << 3) & self.white & self.MASK_NE
                jumps += [0x91 << bit-7 for bit, piece in enumerate(bin(movable)[:1:-1]) if piece == '1']
                movable = (takeable << 5) & self.white & self.MASK_NW
                jumps += [0x211 << bit-9 for bit, piece in enumerate(bin(movable)[:1:-1]) if piece == '1']

            takeable = (empty_squares << 3) & self.black & self.MASK_NE
            if takeable:
                movable = (takeable << 4) & self.white
                jumps += [0x89 << bit-7 for bit, piece in enumerate(bin(movable)[:1:-1]) if piece == '1']

            takeable = (empty_squares << 5) & self.black & self.MASK_NW
            if takeable:
                movable = (takeable << 4) & self.white
                jumps += [0x221 << bit-9 for bit, piece in enumerate(bin(movable)[:1:-1]) if piece == '1']

            kings = self.white & self.kings
            takeable = (empty_squares >> 4) & self.black
            if takeable:
                movable = (takeable >> 3) & kings & self.MASK_SW
                jumps += [0x89 << bit for bit, piece in enumerate(bin(movable)[:1:-1]) if piece == '1']
                movable = (takeable >> 5) & kings & self.MASK_SE
                jumps += [0x221 << bit for bit, piece in enumerate(bin(movable)[:1:-1]) if piece == '1']

            takeable = (empty_squares >> 3) & self.black & self.MASK_SW
            if takeable:
                movable = (takeable >> 4) & kings
                jumps += [0x91 << bit for bit, piece in enumerate(bin(movable)[:1:-1]) if piece == '1']

            takeable = (empty_squares >> 5) & self.black & self.MASK_SE
            if takeable:
                movable = (takeable >> 4) & kings
                jumps += [0x211 << bit for bit, piece in enumerate(bin(movable)[:1:-1]) if piece == '1']

            complete_jumps = set()
            for jump in jumps:
                complete_jumps.update(self.jump_from(jump))
            return list(complete_jumps)

    def update_board(self, jump):
        # Returns what the board would look like after a jump
        empty_squares = np.uint32(~(self.black | self.white))
        if self.side == self.BLACK:
            # Apply jump series to pre jump board state
            black = self.black ^ (jump & ~self.white)
            white = self.white & ~jump
            kings = self.kings ^ (jump & ~self.white) & (self.white & ~jump)

    def jump_from(self, jump):
        empty_squares = np.uint32(~(self.black | self.white))
        if self.side == self.BLACK:
            # Apply jump series to pre jump board state
            black, white, kings = self.update_board(jump)
            piece = empty_squares & jump
            bit = int(np.log2(piece))

            jumps_from = []

            takeable = (empty_squares >> 4) & white
            if (takeable >> 3) & piece & self.MASK_SW:
                jumps_from.append(0x89 << bit)
            if (takeable >> 5) & piece & self.MASK_SE:
                jumps_from.append( 0x221 << bit)

            takeable = (empty_squares >> 3) & white & self.MASK_SW
            if (takeable >> 4) & piece:
                jumps_from.append(0x91 << bit)

            takeable = (empty_squares >> 5) & white & self.MASK_SE
            if (takeable >> 4) & piece:
                jumps_from.append(0x211 << bit)

            if piece & kings:
                takeable = (empty_squares << 4) & white
                if (takeable << 3) & piece & self.MASK_NE:
                    jumps_from.append(0x91 << bit-7)
                if (takeable << 5) & piece & self.MASK_NW:
                    jumps_from.append(0x211 << bit-9)

                takeable = (empty_squares << 3) & white & self.MASK_NE
                if (takeable << 4) & piece:
                    jumps_from.append(0x89 << bit-7)

                takeable = (empty_squares << 5) & white & self.MASK_NW
                if (takeable << 4) & piece:
                    jumps_from.append(0x221 << bit-9)

            if not jumps_from:
                return [jump]
            else:
                jump_sequences = []
                for j in jumps_from:
                    #  print('Consecutive jump:' + str([bit for bit, piece in enumerate(bin(j)[:1:-1]) if piece == '1']))
                    #  print('Sequence:' + str([bit for bit, piece in enumerate(bin((j|jump) & ~piece)[:1:-1]) if piece == '1']))
                    jump_sequences.extend(self.jump_from((j | jump) & ~piece))
                return jump_sequences
        else:
            black, white, kings = self.update_board(jump)

            # Get the moved piece
            piece = empty_squares & jump
            bit = int(np.log2(piece))

            jumps_from = []

            takeable = (empty_squares << 4) & black
            if (takeable << 3) & piece & self.MASK_NE:
                jumps_from.append(0x91 << bit-7)
            if (takeable << 5) & piece & self.MASK_NW:
                jumps_from.append(0x211 << bit-9)

            takeable = (empty_squares << 3) & black & self.MASK_NE
            if (takeable << 4) & piece:
                jumps_from.append(0x89 << bit-7)

            takeable = (empty_squares << 5) & black & self.MASK_NW
            if (takeable << 4) & piece:
                jumps_from.append(0x221 << bit-9)

            if piece & kings:
                takeable = (empty_squares >> 4) & black
                if (takeable >> 3) & piece & self.MASK_SW:
                    jumps_from.append(0x89 << bit)
                if (takeable >> 5) & piece & self.MASK_SE:
                    jumps_from.append(0x221 << bit)

                takeable = (empty_squares >> 3) & black & self.MASK_SW
                if (takeable >> 4) & piece:
                    jumps_from.append(0x91 << bit)

                takeable = (empty_squares >> 5) & black & self.MASK_SE
                if (takeable >> 4) & piece:
                    jumps_from.append(0x211 << bit)

            if not jumps_from:
                return [jump]
            else:
                jump_sequences = []
                for j in jumps_from:
                    #  print('Consecutive jump:' + str([bit for bit, piece in enumerate(bin(j)[:1:-1]) if piece == '1']))
                    #  print('Sequence:' + str([bit for bit, piece in enumerate(bin((j|jump) & ~piece)[:1:-1]) if piece == '1']))
                    jump_sequences.extend(self.jump_from((j | jump) & ~piece))
                return jump_sequences

    def format_move(self, move):
        if self.side == self.BLACK:
            move_from = np.log2(self.black & move)
            if (self.white & move):
                path =  'x{' + ', '.join([str(bit) for bit, piece in enumerate(bin(self.white & move)[:1:-1]) if piece == '1']) + '}'
            else:
                path = '->'
            move_to = np.log2(~(self.black | self.white) & move)
        else:
            move_from = np.log2(self.white & move)
            if (self.black & move):
                path =  'x{' + ', '.join([str(bit) for bit, piece in enumerate(bin(self.black & move)[:1:-1]) if piece == '1']) + '}'
            else:
                path = '->'
            move_to = np.log2(~(self.white | self.black) & move)

        return('{!s:>2} {} {!s:<2}'.format(int(move_from), path, int(move_to)))

    def print_moves(self, moves=None):
        if not moves:
            moves = self.get_moves()
        if self.side == self.BLACK:
            print('Black\'s turn, possible moves:')
            for i, move in enumerate(moves):
                move_from = np.log2(self.black & move)
                if (self.white & move):
                    path =  'x{' + ', '.join([str(bit) for bit, piece in enumerate(bin(self.white & move)[:1:-1]) if piece == '1']) + '}'
                else:
                    path = '->'
                move_to = np.log2(~(self.black | self.white) & move)
                print('  {!s:>2}. {!s:>2} {} {!s:<2}'.format(i, int(move_from), path, int(move_to)))
        else:
            print('White\'s turn, possible moves:')
            for i, move in enumerate(moves):
                move_from = np.log2(self.white & move)
                if (self.black & move):
                    path =  'x{' + ', '.join([str(bit) for bit, piece in enumerate(bin(self.black & move)[:1:-1]) if piece == '1']) + '}'
                else:
                    path = '->'
                move_to = np.log2(~(self.white | self.black) & move)
                print('  {!s:>2}. {!s:>2} {} {!s:<2}'.format(i, int(move_from), path, int(move_to)))

    def update_board(self, move):
        # Return a board with the move applied
        empty_squares = np.uint32(~(self.black | self.white))
        if self.side == self.BLACK:
            jumped = self.white & move
            moved_from = self.black & move
            moved_to = empty_squares & move

            black = (self.black | moved_to) & ~moved_from
            white = self.white & ~jumped

            # Move kings with jump
            kings = self.kings & ~moved_from
            kings = kings & ~jumped
            if moved_from & self.kings:
                kings = kings | moved_to

            return (black, white, kings)
        else:
            jumped = self.black & move
            moved_from = self.white & move
            moved_to = empty_squares & move

            white = (self.white | moved_to) & ~moved_from
            black = self.black & ~jumped

            # Move kings with jump
            kings = self.kings & ~moved_from
            kings = kings & ~jumped
            if moved_from & self.kings:
                kings = kings | moved_to

            return (black, white, kings)

    def make_move(self, move):
        self.black, self.white, self.kings = self.update_board(move)
        # Promote new kings
        self.kings |= self.black & 0xf0000000
        self.kings |= self.white & 0x0000000f

        self.side = ~self.side

    def print_board(self, board=None):
        hchar = '-'
        vchar = '||'
        hline = hchar * 7 * 8 + hchar * 4
        cprint(hline, 'blue', 'on_blue')
        for row in range(8):
            for cellrow in range(3):
                cprint(vchar, 'blue', 'on_blue', end='')
                for col in range(8):
                    #  print(vchar, end='')
                    cellnum = (row * 8 + col)
                    if (row + col) % 2:
                        square = cellnum // 2
                        mask = 1 << (square)
                        if self.black & mask:
                            piece = 'B'
                        elif self.white & mask:
                            piece = 'W'
                        else:
                            piece = ''
                        if piece and (self.kings & mask):
                            piece = '<' + piece + '>'

                        if cellrow == 0:
                            print('{:>7}'.format(square), end='')
                        if cellrow == 1:
                            print('{:^7}'.format(piece), end='')
                        if cellrow == 2:
                            print('{:^7}'.format(''), end='')
                    else:
                        if cellrow == 0:
                            cprint('{:#^7}'.format(''), 'yellow', 'on_yellow', end='')
                        if cellrow == 1:
                            cprint('{:#^7}'.format(''), 'yellow', 'on_yellow', end='')
                        if cellrow == 2:
                            cprint('{:#^7}'.format(''), 'yellow', 'on_yellow', end='')
                cprint(vchar, 'blue', 'on_blue')
        cprint(hline, 'blue', 'on_blue')

class Game:
    def __init__(self):
        modes = ['Player vs Player', 'Player vs Computer', 'Computer vs Computer']
        #  mode = self.prompt('Welcome to checkers! Enter a number to continue.', modes)
        #  self.board = Bitboard()
        rows = []
        for row in range(8):
            rows.append((2**((row+1)*4)-1) - (2**(row*4)-1))
        test_board = {
            'black': rows[3],
            'white': rows[4] + rows[6],
            'kings': 0,
            'side': Bitboard.BLACK
        }
        self.board = Bitboard(preset=test_board)
        print('New game starting...')

        side_names = ['BLACK', 'WHITE']
        while(True):
            self.board.print_board()
            moves = self.board.get_moves()
            if moves:
                move = self.prompt('{}\'s turn, select a move'.format(side_names[self.board.side]),
                        [self.board.format_move(m) for m in moves])
                self.board.make_move(moves[move])
            else:
                self.prompt('{} wins.'.format(side_names[~self.board.side]),
                        ['Play another game', 'Exit'])


    def prompt(self, message, options):
        while True:
            try:
                selection = int(input(message + '\n'
                + '\n'.join(['  {!s:>2}.) {}'.format(i, o) for i, o in enumerate(options)]) + '\n'
                + '--> '))
            except ValueError:
                continue
            if 0 <= selection < len(options):
                return selection
            else:
                continue

game = Game()
#  rows = []
#  for row in range(8):
    #  rows.append((2**((row+1)*4)-1) - (2**(row*4)-1))
#  test_board = {
    #  'black': 2**8,
    #  'white': rows[3] + rows[5] + 2**24 + 2**25 + 2**5,
    #  'kings': 2**8 + 2**13,
    #  'side': Bitboard.BLACK
#  }
#  board = Bitboard(preset=test_board)
#  board.print_board()
#  board.get_moves()
#  board.print_moves()

