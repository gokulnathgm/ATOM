from socketIO_client import SocketIO
import urllib2

socketIO = SocketIO('10.7.90.8', 4000)
#socketIO = SocketIO('localhost', 4000, Namespace)
print socketIO.connected

player1Key = 'T8uhv56xvs'
player2Key = 'GSwwserRd2'
gameKey = '9lVRq6Py7a3Vl1I0c4Fm'

least = 20

def connection_response(*args):
	print args, '\n'

def emit_response(*args):
	print 'Emitted', '\n'

def coin_positions(*args):
	positions = args[0]['position']
	socketIO.emit('player_input', {'position': i, 'force': 4000, 'angle': 90})
	number_of_coins = len(positions)

def oppenent_coins(*args):
	global least
	print 'Opponent coins:\n ', args
	positions = args[0]['position']
	number_of_coins = len(positions)
	if number_of_coins < least:
		least = number_of_coins

socketIO.on('player_input', emit_response)
socketIO.emit('connect_game', {'playerKey': player1Key, 'gameKey': gameKey})
socketIO.on('connect_game', connection_response)

global i
for i in range(194,806):
	response = urllib2.urlopen('http://10.7.90.8:4000/restart-game/9lVRq6Py7a3Vl1I0c4Fm/1')
	socketIO.on('your_turn', coin_positions)
	socketIO.on('opponent_turn', oppenent_coins)
print 'Max number of coins pocketted: ', (20 - least)

socketIO.wait()

