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

	positions = args[0]['position']
	number_of_coins = len(positions)
	print '{}{}'.format('Number of coins = ', number_of_coins) 

	for coin in positions:
		print '{}, {}, {}'.format(coin['x'], coin['y'], coin['type'])

	socketIO.wait(seconds=15)
	position = random.randint(200, 800)
	force = random.randint(2000, 4000)
	angle = random.randint(0, 180)	
	socketIO.emit('player_input', {'position': position, 'force': force, 'angle': angle})

socketIO.emit('connect_game', {'playerKey': player1Key, 'gameKey': gameKey})
socketIO.on('connect_game', connection_response)
socketIO.on('your_turn', coin_positions)
socketIO.wait()