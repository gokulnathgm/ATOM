from socketIO_client import SocketIO
from sympy.geometry import *
from sympy import sympify
import random
import math

socketIO = SocketIO('10.7.90.8', 4000)
print socketIO.connected

player1Key = 'T8uhv56xvs'
player2Key = 'GSwwserRd2'
gameKey = '9lVRq6Py7a3Vl1I0c4Fm'

def distance_between_points(point1, point2):
	x1, y1 = point1[0], point1[1]
	x2, y2 = point2[0], point2[1]
	distance = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
	return distance

def emit_response(*args):
	print 'Emit response'
	print args

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
	print 'Here!!!!'
	position = 300
	force = 4000
	angle = random.randint(20,160)
	socketIO.emit('player_input', {'position': position, 'force': force, 'angle': angle})
	socketIO.on('player_input', emit_response)

socketIO.emit('connect_game', {'playerKey': player2Key, 'gameKey': gameKey})
socketIO.on('connect_game', connection_response)
socketIO.on('your_turn', coin_positions)
socketIO.wait()