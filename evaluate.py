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
	# Get piece it captures.
	piece = 0
	if board.is_capture(move):
		if board.is_en_passant(move):
			piece = 1 # pawn 
		else:
			piece = board.piece_at(move.to_square).piece_type
	return reward[piece]

def branch(board, layers, myturn=True):
	moves = utils.get_all_legal_moves(board)
	vals = {}

	for mv in moves:
		if layers == 0:
			vals[mv.uci()] = value(board, mv)
		else:
			_board = chess.Board(board.fen()) # deep copy of board
			_board.push(mv)
			vals[mv.uci()] = branch(_board, layers-1, not myturn)[1]
	
	arg = max(vals, key=vals.get) if myturn else min(vals, key=vals.get)
	v = vals[arg]
	return arg, v 
 
def eval(board, n, eval_func):
	"""
	Input:
		board - chess.Board object
	Returns:
		A valid move in uci string format.
	"""
	#moves = utils.get_all_legal_moves(board)
	#move = random.choice(moves).uci()
	#print(f"Bot is moving {move}...")
	#return move

	move, val = eval_func(board, 3, True)
	print(f"Bot {n%2 + 1} is moving {move} with payoff {val}...")
	return move
