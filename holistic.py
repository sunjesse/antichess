import random
import chess
import utils
from math import inf
from evaluate import PAWN, KNIGHT, BISHOP, ROOK, QUEEN, KING, WHITE, BLACK

def material_eval(board):
	"""
	Sum up piece values. Black pieces get a negative value, white pieces get a positive value.
	Black aims to get a high negative value, white aims to get a high positive value.	
	Input:
		board: chess.Board object
	Returns:
		Number which signifies which color has a material advantage and by how much.

	"""
	symbol_value_map = {
		'P': 100, 'B': 300, 'N': 300, 'R': 500, 'Q': 900, 'K': 1000,
		'p': -100, 'b': -300, 'n': -300, 'r': -500, 'q': -900, 'k': -1000
	}
	total = 0
	for piece in board.piece_map().values():
		total += symbol_value_map[piece.symbol()]
	return total

def eval_piece_type(board, piece_type, color):
	"""
	Evaluates a position based on the location of a given piece. 
	Depending on the position of a piece, it gets a negative, positive, or zero value.
	Input:
		board: chess.Board object
		piece_type: int, one of PAWN, KNIGHT, BISHOP, QUEEN
		color: boolean, WHITE or BLACK
	Returns:
		Number which signifies which color has a positional advantage and by how much.
	"""
	pawn_eval = [
		200,  200,  200,  200,  200,  200,  200,  200,
		50,  50,  50,  50,  50,  50,  50,  50,
		25,  25,  25,  25,  25,  25,  25,  25,
		0,  0,  0,  0,  0,  0,  0,  0,
		-30,  0,  0,  0,  0,  0,  0,  -30,
		30,  30,  30,  0,  0,  30,  30,  30,
		10,  10,  10,  10,  10,  10,  10,  10,
		0,  0,  0,  0,  0,  0,  0,  0,
	]

	knight_eval = [
		0,  0,  0,  0,  0,  0,  0,  0,
		0,  0,  0,  0,  0,  0,  0,  0,
		0,  0,  0,  0,  0,  0,  0,  0,
		0,  0,  0,  0,  0,  0,  0,  0,
		0,  0,  0,  0,  0,  0,  0,  0,
		0,  0,  50,  0,  0,  50,  0,  0,
		0,  0,  0,  50,  50,  0,  0,  0,
		0,  0,  0,  0,  0,  0,  0,  0,
	]

	bishop_eval = [
		0,  0,  0,  0,  0,  0,  0,  0,
		0,  0,  0,  0,  0,  0,  0,  0,
		0,  0,  0,  0,  0,  0,  0,  0,
		0,  0,  0,  0,  0,  0,  0,  0,
		0,  0,  0,  0,  0,  0,  0,  0,
		0,  0,  0,  0,  0,  0,  0,  0,
		0,  20,  0,  0,  0,  0,  20,  0,
		0,  0,  0,  0,  0,  0,  0,  0,
	]

	rook_eval = [
		0,  0,  0,  0,  0,  0,  0,  0,
		40,  40,  0,  0,  0,  0,  40,  40,
		0,  0,  0,  0,  0,  0,  0,  0,
		0,  0,  0,  0,  0,  0,  0,  0,
		0,  0,  0,  0,  0,  0,  0,  0,
		50,  0,  0,  0,  0,  0,  0,  50,
		30,  0,  0,  0,  0,  0,  0,  30,
		20,  0,  50,  50,  50,  50,  0,  20,
	]

	queen_eval = [
		0,  0,  0,  0,  0,  0,  0,  0,
		0,  0,  0,  0,  0,  0,  0,  0,
		0,  0,  0,  0,  0,  0,  0,  0,
		0,  0,  0,  0,  0,  0,  0,  0,
		0,  0,  0,  0,  0,  0,  0,  0,
		0,  0,  0,  0,  0,  0,  0,  0,
		0,  0,  0,  0,  0,  0,  0,  0,
		0,  0,  0,  0,  0,  0,  0,  0,
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
		evaluation += (eval_matrix[piece_type][::-1][piece] if color == WHITE else eval_matrix[piece_type][piece])

	return evaluation

def piecewise_eval(board):
	return eval_piece_type(board, PAWN, board.turn) \
				+ eval_piece_type(board, KNIGHT, board.turn) \
				+ eval_piece_type(board, BISHOP, board.turn) \
				+ eval_piece_type(board, ROOK, board.turn) \
				+ eval_piece_type(board, QUEEN, board.turn)

def eval_board(board):
	return material_eval(board) + 0.3 * piecewise_eval(board)


def recurse_max(board, layers, alpha=-inf, beta=inf, transpositions=dict()):
	# Check all moves
	moves = utils.get_all_legal_moves(board)

	# Maintain a local maximum
	local_max = -inf
	best_move = moves[0]
	vals = dict()

	# Don't end on a capture move
	if layers == 0 and utils.get_capture_moves(board) == moves:
		layers += 1

	for move in moves:
		# Check if we reached maximum depth
		if layers == 0:
			val = eval_board(board)
			if val > local_max:
				local_max = val
				best_move = move
			continue

		_board = board.copy()					# Copy board so we can manipulate it
		_board.push(move) 						# Make the move

		# Check termination conditions
		outcome = _board.outcome()
		if outcome:
			if outcome.winner == None:	# No winner, so it's a stalemate
				val = 0
			elif outcome.winner:				# White wins, so we return high positive value
				val = inf
			else:
				val = -inf								# Black wins, so we return high negative value
		else:
			# Evaluate minimum value for the move to get next player's move
			# Either choose the cached value or calculate it
			if _board.fen() in transpositions:
				val = transpositions[_board.fen()]
			else:
				val = recurse_min(_board, layers - 1, alpha, beta, transpositions)[1]
				transpositions[_board.fen()] = val

		vals[move.uci()] = val
		# Update the local maximum and store the best move as needed
		if val > local_max:
			local_max = val
			best_move = move
		elif val == local_max:
			chosen_move = random.choice([(best_move, local_max), (move, val)])
			best_move = chosen_move[0]
			local_max = chosen_move[1]

		if local_max >= beta:
			break

		alpha = max(local_max, alpha)
	
	return best_move.uci(), local_max

def recurse_min(board, layers, alpha=-inf, beta=inf, transpositions=dict()):
	# Check all moves
	moves = utils.get_all_legal_moves(board)

	# Maintain a local maximum
	local_min = inf
	best_move = moves[0]
	vals = dict()

	# Don't end on a capture move
	if layers == 0 and utils.get_capture_moves(board) == moves:
		layers += 1

	for move in moves:
		# Check if we reached maximum depth
		if layers == 0:
			val = eval_board(board)
			if val < local_min:
				local_min = val
				best_move = move
			continue

		_board = board.copy() 	# Copy board so we can manipulate it
		_board.push(move) 			# Make the move

		# Check termination conditions
		outcome = _board.outcome()
		if outcome:
			if outcome.winner == None: # No winner, so it's a stalemate
				val = 0
			elif outcome.winner: 			 # White wins, so we return high positive value
				val = inf
			else:
				val = -inf		 					 # Black wins, so we return high negative value
		else:
			# Evaluate maximum value for the move to get next player's move
			# Either choose the cached value or calculate it
			if _board.fen() in transpositions:
				val = transpositions[_board.fen()]
			else:
				val = recurse_max(_board, layers - 1, alpha, beta, transpositions)[1]
				transpositions[_board.fen()] = val

		vals[move.uci()] = val
		# Update the local minimum and store the best move as needed
		if val < local_min:
			local_min = val
			best_move = move
		elif val == local_min:
			chosen_move = random.choice([(best_move, local_min), (move, val)])
			best_move = chosen_move[0]
			local_min = chosen_move[1]

		if local_min <= alpha:
			break

		beta = min(local_min, beta)

	return best_move.uci(), local_min


def holistic(board, layers=3):
	"""
	Strategy that accounts for material difference and piece positioning.
	Input:
		board : chess.Board object
		layers : layers of the tree we branch into
	Returns:
		(str, int) : Returns the optimal move along with corresponding board eval.
	"""

	# Start with min or max depending on player
	if board.turn == WHITE:
		# Hardcode starting move to make it easier
		if len(board.move_stack) == 0:
			return 'a2a3', 0
		return recurse_max(board, layers)
	return recurse_min(board, layers)
