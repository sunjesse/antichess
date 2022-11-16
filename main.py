import chess
import argparse
import utils
from evaluate import eval

def parse_args():
	parser = argparse.ArgumentParser()
	parser.add_argument('--bf', action='store_true', help="Assign bot to player 1.")
	return parser.parse_args()
	

def is_valid_move(board, move):
	if not board.is_legal(move):
		print("Invalid move! Try again.")
		return False

	# check if current player can capture a piece. If there exists such a move,
	# the player must play a capture move.
	capture_moves = list(filter(lambda mv : board.is_capture(mv), board.legal_moves))
	if len(capture_moves) > 0 and move not in capture_moves:
		print(f"Invalid mode.\nPlace a capture move from {[x.uci() for x in capture_moves]}")
		return False
				
	return True	
	
def is_game_over(board, n):
	end = board.is_checkmate() or board.is_stalemate() or board.is_repetition() 	
	if n >= 50:
		end = end or board.is_fifty_moves()
	return end

def play(args):
	n = 0
	board = chess.Board()
	print(board)
	while not is_game_over(board, n):
		if n % 2 == 0:  # player 1 turn
			_move = eval(board, n) if args.bf else utils.get_input(n)
		else: # player 2 turn
			_move = utils.get_input(n) if args.bf else eval(board, n) 
				
		try:
			move = chess.Move.from_uci(_move)
			if is_valid_move(board, move): 
				board.push(move)
				n += 1
				print(board)
		except:
			print("Invalid input. Input standard algebraic notation move.")

if __name__ == '__main__':
	args = parse_args()
	play(args)
