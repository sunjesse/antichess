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

def sumbased(board, layers=4, myturn=True):
	"""
	Strategy that accounts for king safety, material loss, etc.
	Input:
		board : chess.Board object
		layers : layers of the tree we branch into
		myturn : boolean that determines if the current layer is the bot's move.
				 Use to determine whether we should min or max.
	Returns:
		(str, int) : Returns the optimal move along with corresponding value.
	"""

	symbol_value_map = {
		'P': 100, 'B': 300, 'N': 300, 'R': 500, 'Q': 900, 'K': 1000,
		'p': -100, 'b': -300, 'n': -300, 'r': -500, 'q': -900, 'k': -1000
	}

	def material_eval(board):
		"""
		Sum up piece values. Black pieces get a negative value, white pieces get a positive value.
		Black aims to get a high negative value, white aims to get a high positive value.	
		"""
		total = 0
		for piece in board.piece_map().values():
			total += symbol_value_map[piece.symbol()]
		return total

	def eval_piece_type(board, piece_type, color):
		# Values from https://www.chessprogramming.org/Simplified_Evaluation_Function
		pawn_eval = [
			0,  0,  0,  0,  0,  0,  0,  0,
			50, 50, 50, 50, 50, 50, 50, 50,
			10, 10, 20, 30, 30, 20, 10, 10,
			5,  5, 10, 25, 25, 10,  5,  5,
			0,  0,  0, 20, 20,  0,  0,  0,
			5, -5,-10,  0,  0,-10, -5,  5,
			5, 10, 10,-20,-20, 10, 10,  5,
			0,  0,  0,  0,  0,  0,  0,  0
		]

		knight_eval = [
			-50,-40,-30,-30,-30,-30,-40,-50,
			-40,-20,  0,  0,  0,  0,-20,-40,
			-30,  0, 10, 15, 15, 10,  0,-30,
			-30,  5, 15, 20, 20, 15,  5,-30,
			-30,  0, 15, 20, 20, 15,  0,-30,
			-30,  5, 10, 15, 15, 10,  5,-30,
			-40,-20,  0,  5,  5,  0,-20,-40,
			-50,-40,-30,-30,-30,-30,-40,-50,
		]

		bishop_eval = [
			-20,-10,-10,-10,-10,-10,-10,-20,
			-10,  0,  0,  0,  0,  0,  0,-10,
			-10,  0,  5, 10, 10,  5,  0,-10,
			-10,  5,  5, 10, 10,  5,  5,-10,
			-10,  0, 10, 10, 10, 10,  0,-10,
			-10, 10, 10, 10, 10, 10, 10,-10,
			-10,  5,  0,  0,  0,  0,  5,-10,
			-20,-10,-10,-10,-10,-10,-10,-20,
		]

		rook_eval = [
			0,  0,  0,  0,  0,  0,  0,  0,
			5, 10, 10, 10, 10, 10, 10,  5,
			-5,  0,  0,  0,  0,  0,  0, -5,
			-5,  0,  0,  0,  0,  0,  0, -5,
			-5,  0,  0,  0,  0,  0,  0, -5,
			-5,  0,  0,  0,  0,  0,  0, -5,
			-5,  0,  0,  0,  0,  0,  0, -5,
			0,  0,  0,  5,  5,  0,  0,  0
		]

		queen_eval = [
			-20,-10,-10, -5, -5,-10,-10,-20,
			-10,  0,  0,  0,  0,  0,  0,-10,
			-10,  0,  5,  5,  5,  5,  0,-10,
			-5,  0,  5,  5,  5,  5,  0, -5,
				0,  0,  5,  5,  5,  5,  0, -5,
			-10,  5,  5,  5,  5,  5,  0,-10,
			-10,  0,  5,  0,  0,  0,  0,-10,
			-20,-10,-10, -5, -5,-10,-10,-20
		]


		# Evaluate the total value of all the piece positions
		pieces = board.pieces(piece_type, color)
		evaluation = 0

		eval_matrix = {
			PAWN: pawn_eval,
			KNIGHT: knight_eval,
			BISHOP: bishop_eval,
			ROOK: rook_eval,
			QUEEN: queen_eval
		}

		for piece in pieces:
			evaluation += (eval_matrix[piece_type][piece] if color == WHITE else eval_matrix[piece_type][::-1][piece])

		return evaluation

	def piecewise_eval(board):
		return eval_piece_type(board, PAWN, board.turn) \
					+ eval_piece_type(board, KNIGHT, board.turn) \
					+ eval_piece_type(board, BISHOP, board.turn) \
					+ eval_piece_type(board, ROOK, board.turn) \
					+ eval_piece_type(board, QUEEN, board.turn)

	def eval_board(board):
		return material_eval(board) + 0.1 * piecewise_eval(board)
	
	def recurse_max(board, layers, alpha=-inf, beta=inf):
		# Maintain a local maximum
		local_max = -inf
		best_move = None

		# Check all moves
		moves = utils.get_all_legal_moves(board)
		for move in moves:
			# Check if we reached maximum depth
			if layers == 0:
				return move.uci(), eval_board(board)

			_board = chess.Board(board.fen()) 	# Copy board so we can manipulate it
			_board.push(move) 									# Make the move

			# Check termination conditions
			outcome = _board.outcome()
			if outcome:
				if outcome.winner == None: # No winner, so it's a stalemate
					return move.uci(), 0
				elif outcome.winner: 			 # White wins, so we return high positive value
					return move.uci(), inf
				return move.uci(), -inf		 # Black wins, so we return high negative value

			# Evaluate minimum value for the move to get next player's move
			val = recurse_min(_board, layers - 1, alpha, beta)[1]

			# Update the local maximum and store the best move as needed
			if val > local_max:
				local_max = val
				best_move = move.uci()

			if local_max >= beta:
				return move.uci(), local_max

			alpha = max(local_max, alpha)
		
		return best_move, local_max

	def recurse_min(board, layers, alpha=-100, beta=100):
			# Maintain a local maximum
		local_min = inf
		best_move = None

		# Check all moves
		moves = utils.get_all_legal_moves(board)
		for move in moves:
			# Check if we reached maximum depth
			if layers == 0:
				return move.uci(), eval_board(board)

			_board = chess.Board(board.fen()) 	# Copy board so we can manipulate it
			_board.push(move) 									# Make the move

			# Check termination conditions
			outcome = _board.outcome()
			if outcome:
				if outcome.winner == None: # No winner, so it's a stalemate
					return move.uci(), 0
				elif outcome.winner: 			 # White wins, so we return high positive value
					return move.uci(), inf
				return move.uci(), -inf		 # Black wins, so we return high negative value

			# Evaluate maximum value for the move to get next player's move
			val = recurse_max(_board, layers - 1, alpha, beta)[1]

			# Update the local minimum and store the best move as needed
			if val < local_min:
				local_min = val
				best_move = move.uci()

			if local_min <= alpha:
				return best_move, local_min

			beta = min(local_min, beta)
		
		return best_move, local_min

	# Start with min or max depending on player
	if board.turn:
		return recurse_max(board, layers)
	return recurse_min(board, layers)

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
			v = value(_board, mv)
			_board.push(mv)
			if _board.is_checkmate():
				vals[mv.uci()] = 100 # assign checkmate arbitrary high value
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
