import chess
import argparse
import utils
from evaluate import eval, branch

def parse_args():
	parser = argparse.ArgumentParser()
	parser.add_argument('--bf', action='store_true', help="Assign bot to player 1.")
	parser.add_argument('--bvb', action='store_true', help="Bot vs bot.")
	return parser.parse_args()
	

def is_valid_move(board, move):
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
		if args.bvb: # play bot vs bot
			_move = eval(board, n, branch)
		else:
			if n % 2 == 0:  # player 1 turn
				_move = eval(board) if args.bf else utils.get_input(n)
			else: # player 2 turn
				_move = utils.get_input(n) if args.bf else eval(board) 

		try:
			is_bot_turn = ((n % 2 == 0) and args.bf) or ((n%2 == 1) and not args.bf) 
			move = chess.Move.from_uci(_move)
			# do not need to check if bot move is valid
			# as it chooses from a valid move.
			if is_bot_turn:
				board.push(move)
				n += 1
				print(board)

			elif is_valid_move(board, move): 
				board.push(move)
				n += 1
				print(board)

		except:
			print("Invalid input. Input standard algebraic notation move.")

	print(f"\nPlayer {(n+1) % 2 + 1} won!")

if __name__ == '__main__':
	args = parse_args()
	play(args)
