import time
import chess
import utils
from evaluate import WHITE, eval
from holistic import holistic
import sys

def is_valid_move(board, move):
	"""
	Check if "move" (chess.Move object) is valid anti-chess move.
	That is, first check if it is legal according to chess moves,
	then it must obey the anti-chess rule where it must be a
	capture move if a capture move is available.
	"""
	if not board.is_legal(move):
		#print("Invalid move! Try again.")
		return False

	# check if current player can capture a piece. If there exists such a move,
	# the player must play a capture move.
	capture_moves = utils.get_capture_moves(board)
	if len(capture_moves) > 0 and move not in capture_moves:
		#print(f"Invalid mode. Place a capture move from {[x.uci() for x in capture_moves]}")
		return False
				
	return True
	
def play():
	n = 0
	board = chess.Board()
		
	color = sys.argv[1]
	assert color in ['white', 'black'], f"{color} is not a valid piece color."
	is_white = (color == "white")

	while not board.is_game_over():
		if n % 2 == 0:  # player 1 turn
			_move = eval(board, n, holistic) if is_white else utils.get_input(n)
		else: # player 2 turn
			_move = utils.get_input(n) if is_white else eval(board, n, holistic)

		try:
			is_bot_turn = ((n % 2 == 0) and is_white) or ((n%2 == 1) and not is_white) 
			move = chess.Move.from_uci(_move)
			# do not need to check if bot move is valid
			# as it chooses from a valid move.
			if is_bot_turn:
				board.push(move)
				n += 1

			elif is_valid_move(board, move): 
				board.push(move)
				n += 1

		except Exception as e:
			continue
	
	outcome = board.outcome(claim_draw=True)
	#if outcome.winner == None:
	#	print("Stalemate!")
	#elif outcome.winner == WHITE:
	#	print(f"\nWhite wins!")
	#else:
	#	print(f"\nBlack wins!")

if __name__ == '__main__':
	play()
