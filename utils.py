def get_input(n):
	return str(input(f"Move for player {n % 2 + 1}: "))

def get_capture_moves(board):
	"""
	Input:
		board - chess.Board object. It describes the current state of the board.
	Returns:
		list - list of capture moves
	"""
	return list(filter(lambda mv : board.is_capture(mv), board.legal_moves))

def get_all_legal_moves(board):
	"""
	Input:
		board - chess.Board object
	Returns:
		list - list of moves the bot can make.
	
	If capture moves exists, the bot must make a capture move. Otherwise, the
	bot can make any legal chess move.

	We use this function to generate moves we can branch on.
	"""
	cm = get_capture_moves(board)
	if len(cm) > 0:
		return cm

	return list(board.legal_moves)
