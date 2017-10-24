import numpy as np
from termcolor import colored, cprint

class Bitboard:
    
    BLACK, WHITE = 0, 1

    # All even row squares can move to the left and all odd row squares 
    #   can move to the right with a bitshift of 4. The following masks define
    #   squares from which pieces can perform bitshifts of 3 and 5.

    # Even rows: 0x07 -> 0b00000111 
    MASK_L5 = 0x07070707 # southeast
    MASK_R3 = 0x07070700 # northeast
    
    # Odd rows: 0xe0 -> 0b11100000
    MASK_L3 = 0x00e0e0e0 # southwest
    MASK_R5 = 0xe0e0e0e0 # northwest
    
    def __init__(self, preset=None):
        if preset:
            self.black = preset.black
            self.white = preset.white
            self.kings = preset.kings
        else:
            self.black = np.int32(2**12-1 + 2**16)
            self.white = np.int32(2**32 - 2**20)
            self.kings = np.uint32(2**16)
        self.active = self.BLACK

    def get_moves(self, side):
        empty_squares = ~(self.black | self.white)
        if side == BLACK:
            kings = self.black & self.kings
            movable = (empty_squares >> 4) & self.black
            movable |= (empty_squares >> 3) & self.black & MASK_L3
            movable |= (empty_squares >> 5) & self.black & MASK_L5
            movable |= (empty_squares << 4) & kings
            movable |= (empty_squares << 3) & kings & MASK_R3
            movable |= (empty_squares << 5) & kings & MASK_R5
            return movable; 
        else:
            kings = self.white & self.kings
            movable = (empty_squares << 4) & self.white
            movable |= (empty_squares << 3) & self.white & MASK_R3
            movable |= (empty_squares << 5) & self.white & MASK_R5
            movable |= (empty_squares >> 4) & kings
            movable |= (empty_squares >> 3) & kings & MASK_L3
            movable |= (empty_squares >> 5) & kings & MASK_L5
            return movable; 

    def get_jumps(self):
        pass

    def display(self, board=None):
        hchar = '-'
        vchar = '|'
        hline = (' ' + hchar * 7) * 8
        print(hline)
        #  move = self.get_moves()
        for row in range(8):
            for cellrow in range(3):
                for col in range(8):
                    print(vchar, end='')
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

                        #  if piece and move:
                           #  pass 

                        if cellrow == 0:
                            print('{:>7}'.format(square), end='')
                        if cellrow == 1:
                            print('{:^7}'.format(piece), end='')
                        if cellrow == 2:
                            print('{:^7}'.format(''), end='')
                    else:
                        if cellrow == 0:
                            print('{:#>7}'.format(''), end='')
                        if cellrow == 1:
                            print('{:#^7}'.format(''), end='')
                        if cellrow == 2:
                            print('{:#^7}'.format(''), end='')
                print(vchar)
            print(hline)

class Move:
    def __init__(self):
        pass

board = Bitboard()
board.display()

