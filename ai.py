import numpy as np
import time
from checkers import Bitboard, count_bits
import signal

class AI:
    def __init__(self, timelimit=5):
        self.timelimit = timelimit
        self.transposition = {}

    def timer(self, signum, frame):
        raise Exception('IDSTimeout')

    def ids(self, board):
        # iterative deepening search
        signal.signal(signal.SIGALRM, self.timer)
        signal.alarm(self.timelimit)
        self.start = time.time()
       
        try:
            self.maxdepth = 1
            self.side = board.side
            
            moves = board.get_moves()
            if len(moves) == 1:
                signal.alarm(0)
                return moves[0]

            # Set to 0 when game tree fully explored
            self.unexplored = 1
            while self.unexplored:
                scores = self.minimax(board, moves, self.maxdepth)
                selected = np.argmax(scores)
                #  for i, move in enumerate(moves):
                    #  if i == selected:
                        #  print('*', end='')
                    #  print('{!r} {} | '.format([bit for bit, piece in enumerate(bin(move)[:1:-1]) if piece == '1'], scores[i]), end='')
                #  print()
                move = moves[np.argmax(scores)]
                moves = [moves[i] for i in np.argsort(-np.array(scores))]

                score = self.evaluate(Bitboard(board.get_state()).make_move(move))
                elapsed = time.time() - self.start
                #  print('Depth {} : {}s elapsed, move {} selected, score = {}'.format(maxdepth, elapsed, board.format_move(move), score))
                if elapsed > self.timelimit / 2:
                    break
                self.maxdepth += 1    
            
            print('  Search depth reached: ', self.maxdepth)
            signal.alarm(0)
            return move

        except Exception as inst:
            if inst.args[0] == 'IDSTimeout':
                #  print('{}s time limit reached! Returning last iteration\'s move.'.format(self.timelimit))
                print('  Search depth reached: ', self.maxdepth)
                return move
            else:
                raise
    
    def minimax(self, board, moves, depth):
        # minimax with alpha beta pruning, returns a list of scores
        self.unexplored = 0
        if len(moves) == 0:
            # terminal state
            return self.evaluate(board)
        if not depth:
            self.unexplored = 1
            return self.evaluate(board)
        values = []
        v = float('-inf')
        alpha, beta = float('-inf'), float('inf')
        for move in moves:
            new_board = Bitboard(board.get_state()).make_move(move)
            min_value = self.min_value(new_board, depth - 1, alpha, beta)
            values.append(min_value)
            v = max(v, min_value)
            alpha = max(alpha, v)
            if beta <= alpha:
                break
        return values

    def max_value(self, board, depth, alpha, beta):
        moves = board.get_moves()
        if len(moves) == 0:
            return self.evaluate(board)
        if not depth:
            self.unexplored = 1
            return self.evaluate(board)
        value = float('-inf') # np.NINF
        for move in moves:
            new_board = Bitboard(board.get_state()).make_move(move)
            min_value = self.min_value(new_board, depth - 1, alpha, beta)
            value = max(value, min_value)
            alpha = max(alpha, value)
            if beta <= alpha:
                break
        return value

    def min_value(self, board, depth, alpha, beta):
        moves = board.get_moves()
        if len(moves) == 0:
            return self.evaluate(board)
        if not depth:
            self.unexplored = 1
            return self.evaluate(board)
        value = float('inf') # np.inf
        for move in moves:
            new_board = Bitboard(board.get_state()).make_move(move)
            max_value = self.max_value(new_board, depth - 1, alpha, beta)
            value = min(value, max_value)
            beta = min(beta, value)
            if beta <= alpha:
                break
        return value

    def evaluate(self, board):
        score = 0

        # Piece counts to determine game phase
        npieces = count_bits(board.black) + count_bits(board.white)
        nkings = count_bits(board.kings)
        nmen = npieces - nkings
        
        # Early-mid game is classified as when there are pawns or more than 5 pieces
        if nmen or npieces > 5:
            # Material advantage
            material_black = count_bits(board.black) + count_bits(board.black & board.kings) * .5 
            material_white = count_bits(board.white) + count_bits(board.white & board.kings) * .5
            
            # Favor trades when ahead in material. Max material on the board is 36
            exchange = (37 - material_black - material_white)
            score += (material_black - material_white) * exchange * 5

            # Advancement
            score += (board.black & 0xfffff000 - board.white & 0x000fffff) * 10

            # Central kings
            score += (board.black & board.kings & 0x00666600 - board.white & board.kings & 0x00666600) * 20
            
            # King defense
            score += (count_bits(board.black & 0x0000000f) - count_bits(board.white & 0xf0000000)) * 10
            

        # Endgame, 5 kings or fewer
        else:
            king_advantage = count_bits(board.black) - count_bits(board.white)
            exchange = 7.5 - count_bits(board.black) - count_bits(board.white)
            score += king_advantage * exchange * 20
            
            #  Favor attacking with advantage in endgame
            score -= king_advantage * self.total_distance(board.black, board.white)
            
            score += (count_bits(board.black & 0x88000011) - count_bits(board.white & 0x88000011)) * 50
            #  if self.side == board.BLACK:
                #  # Attempt evict defensive enemy kings from corner
                #  if king_advantage:
                    #  score -= count_bits(board.white & 0x88000011) * 100
            #  else:
                
                    #  score += count_bits(board.black & 0x88000011) * 100
        
        # Phase agnostic heuristics

        # Turn advantage
        if board.side == board.BLACK:
            score += 3
        else:
            score -= 3
        
        # Heuristic is symmetric
        return score if self.side == board.BLACK else -1 * score

    def total_distance(self, black, white):
        # Sum of the manhattan distances between pieces
        total = 0
        for bit1, piece in enumerate(bin(black)[:1:-1]):
            if piece == '1':
                for bit2, piece in enumerate(bin(white)[:1:-1]):
                    if piece == '1':
                        rank1, file1 = divmod(bit1, 4)
                        rank2, file2 = divmod(bit2, 4)

                        if bit1 & 0x0f0f0f0f:
                            file1 = file1 * 2 + 1
                        else:
                            file1 = file1 * 2
                        if bit2 & 0x0f0f0f0f:
                            file2 = file2 * 2 + 1
                        else:
                            file2 = file2 * 2
                        
                        total += abs(file2 - file1) + abs(rank2 - rank1)
        return total
