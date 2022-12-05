import chess
import utils
import random
from math import inf

PAWN = 1
KNIGHT = 2
BISHOP = 3
ROOK = 4
QUEEN = 5
KING = 6
WHITE = True
BLACK = False

reward = {
	PAWN: 1, # pawn 1
	KNIGHT: 3, # knight 3
	BISHOP: 3, # bishop 3
	ROOK: 5, # rook 5
	QUEEN: 9, # queen 9
	KING: 10, # king 10
	0: 0 # no piece
}

def value(board, move):
	"""
	Input:
		board : chess.Board object
		move : chess.Move object
	Returns:
		int : Reward/value of making "move" on current "board" 
	"""
	piece = 0
	if board.is_capture(move):
		if board.is_en_passant(move):
			piece = 1 # pawn 
		else:
			piece = board.piece_at(move.to_square).piece_type
	return reward[piece]

def branch(board, layers=4, myturn=True):
	"""
	Min-max strategy. (No bounding/alpha-beta pruning, so we can make more efficient)

	Input:
		board : chess.Board object
		layers : layers of the tree we branch into
		myturn : boolean that determines if the current layer is the bot's move.
				 Use to determine whether we should min or max.
	Returns:
		(str, int) : Returns the optimal move along with corresponding value.
	"""
	moves = utils.get_all_legal_moves(board)
	vals = {}
	
	for mv in moves:
		if layers == 0:
			vals[mv.uci()] = value(board, mv)
		else:
			_board = chess.Board(board.fen()) # deep copy of board
			v = value(_board, mv)
			_board.push(mv)
			if _board.is_checkmate():
				vals[mv.uci()] = 1000 # assign checkmate arbitrary high value
			elif _board.is_stalemate():
				vals[mv.uci()] = -100 # assign stalemate low value since we stalemate other player wins
			else:
				vals[mv.uci()] = branch(_board, layers-1, not myturn)[1] + v # should we add reward for mv?

	arg = max(vals, key=vals.get) if myturn else min(vals, key=vals.get)
	v = vals[arg]
	return arg, v 
 
def randomized(board, layers, myturn=True):
	"""
	Return a random move from list of valid antichess moves.

	Input:
		board : class.Board object
		The remaining two params are actually useless,
		just kept it to make func call same lol.
		TODO: handle same signatures but not in
		dumb way like this?
	Returns:
		(str, int) : move and value of the move
	"""
	moves = utils.get_all_legal_moves(board)
	move = random.choice(moves)
	return move.uci(), value(board, move)

def eval(board, n, eval_func):
	"""
	Input:
		board : chess.Board object
		n : move number. Used to log which bot (if more than 1) is making the move.
		eval_func : evaluation function

	Returns:
		A valid move in uci string format.
	"""
	move, val = eval_func(board)
	print(f"Bot {n%2 + 1} is moving {move} with payoff {val}...")
	return move
