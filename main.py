import time
import chess
import argparse
import utils
from chessboard import display
from evaluate import WHITE, eval
from holistic import holistic


def parse_args():
	parser = argparse.ArgumentParser()
	parser.add_argument('--bf', action='store_true', help="Assign bot to player 1.")
	parser.add_argument('--bvb', action='store_true', help="Bot vs bot.")
	return parser.parse_args()
	

def is_valid_move(board, move):
	"""
	Check if "move" (chess.Move object) is valid anti-chess move.
	That is, first check if it is legal according to chess moves,
	then it must obey the anti-chess rule where it must be a
	capture move if a capture move is available.
	"""
	if not board.is_legal(move):
		print("Invalid move! Try again.")
		return False

	# check if current player can capture a piece. If there exists such a move,
	# the player must play a capture move.
	capture_moves = utils.get_capture_moves(board)
	if len(capture_moves) > 0 and move not in capture_moves:
		print(f"Invalid mode. Place a capture move from {[x.uci() for x in capture_moves]}")
		return False
				
	return True
	
def play(args):
	n = 0
	board = chess.Board()
	display_board = display.start(board.fen())
	while not board.is_game_over():
		if args.bvb: # play bot vs bot
			if n % 2 == 0:  # player 1 is branch
				_move = eval(board, n, holistic)
			else: # player 2 is randomized
				_move = eval(board, n, holistic)
		else:
			if n % 2 == 0:  # player 1 turn
				_move = eval(board, n, holistic) if args.bf else utils.get_input(n)
			else: # player 2 turn
				_move = utils.get_input(n) if args.bf else eval(board, n, holistic)

		try:
			is_bot_turn = ((n % 2 == 0) and args.bf) or ((n%2 == 1) and not args.bf) 
			move = chess.Move.from_uci(_move)
			# do not need to check if bot move is valid
			# as it chooses from a valid move.
			if is_bot_turn:
				board.push(move)
				n += 1
				display.update(board.fen(), display_board)

			elif is_valid_move(board, move): 
				board.push(move)
				n += 1
				display.update(board.fen(), display_board)

		except Exception as e:
			print("Invalid input. Input standard algebraic notation move.")
	
	outcome = board.outcome()
	if outcome.winner == None:
		print("Stalemate!")
	elif outcome.winner == WHITE:
		print(f"\nWhite wins!")
	else:
		print(f"\nBlack wins!")
	display.terminate()


if __name__ == '__main__':
	args = parse_args()
	play(args)
