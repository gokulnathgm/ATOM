from socketIO_client import SocketIO
from sympy.geometry import *
from sympy import sympify
import random

socketIO = SocketIO('10.7.90.8', 4000)
#socketIO = SocketIO('localhost', 4000)
print socketIO.connected

player1Key = 'T8uhv56xvs'
player2Key = 'GSwwserRd2'
gameKey = '9lVRq6Py7a3Vl1I0c4Fm'

# player1Key = 'p21'
# player2Key = 'p22'
# gameKey = '2'

def emit_response(*args):
	print 'Emit response'
	print args

def connection_response(*args):
	print 'connection_response'
	print args

def coin_positions(*args):
	print 'coin positions'
	print args, '\n'

	position = random.randint(200, 800)
	angle = random.randint(0, 180)	
	socketIO.emit('player_input', {'position': position, 'force': 4000, 'angle': angle})
	socketIO.on('player_input', emit_response)

socketIO.emit('connect_game', {'playerKey': player2Key, 'gameKey': gameKey})
socketIO.on('connect_game', connection_response)
socketIO.on('your_turn', coin_positions)
socketIO.wait()
