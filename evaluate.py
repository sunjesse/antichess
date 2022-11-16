import chess
import utils
import random

reward = {
	1: 1, # pawn 1
	2: 2, # knight 2
	4: 3, # rook 4
	3: 4, # bishop 3
	5: 5, # queen 5
	6: 6, # king 6
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

def branch(board, layers=3, myturn=True):
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
			_board.push(mv)
			if utils.is_game_over(_board):
				vals[mv.uci()] = 10
			else:
				vals[mv.uci()] = branch(_board, layers-1, not myturn)[1]
	
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
	move, val = eval_func(board, 3, True)
	print(f"Bot {n%2 + 1} is moving {move} with payoff {val}...")
	return move
