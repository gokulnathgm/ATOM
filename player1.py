from socketIO_client import SocketIO
from sympy.geometry import *
from sympy import sympify
import random

socketIO = SocketIO('10.7.90.8', 4000)
print socketIO.connected

player1Key = 'T8uhv56xvs'
player2Key = 'GSwwserRd2'
gameKey = '9lVRq6Py7a3Vl1I0c4Fm'

def connection_response(*args):
	print 'connection_response'
	print args

def coin_positions(*args):
	print 'coin positions'
	print args

	striker_x = 153.2258
	striker_y = 193.5484
	pocket4_x = 967.7419
	pocket4_y = 967.7419 
	pocket4_point = (pocket4_x, pocket4_y)

	positions = args[0]['position']
	number_of_coins = len(positions)
	print '{}{}'.format('Number of coins = ', number_of_coins) 
	for coin in positions:
		coin_x = coin['x']
		coin_y = coin['y']
		coin_point = (coin_x, coin_y)
		Line_coin_pocket = Line(coin_point, pocket4_point)
		path = True
		for coin_subset in positions:
			coin_subset_x = coin_subset['x']
			coin_subset_y = coin_subset['y']
			coin_subset_point = (coin_subset_x, coin_subset_y)
			if (coin_x != coin_subset_x) and (coin_y != coin_subset_y) and (coin_subset_x > coin_x) and (coin_subset_y > coin_y) and (coin['type'] != 'stricker'):
				path_len = float(Line_coin_pocket.perpendicular_segment(coin_subset_point).length)
				print '{}{} to {}{} = {}'.format(coin_point, coin['type'], coin_subset_point, coin_subset['type'], path_len)
		print '\n'

	# if path:
	# 	print '{}{}'.format('Path exists: ', coin_point)
	# else:
	# 	print '{}{}'.format('No path: ', coin_point)

	socketIO.wait(seconds=15)
	position = 250#random.randint(200, 800)
	force = 2500#random.randint(2000, 4000)
	angle = 130#random.randint(0, 180)	
	socketIO.emit('player_input', {'position': position, 'force': force, 'angle': angle})

socketIO.emit('connect_game', {'playerKey': player1Key, 'gameKey': gameKey})
socketIO.on('connect_game', connection_response)
socketIO.on('your_turn', coin_positions)
socketIO.wait()