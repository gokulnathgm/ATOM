from socketIO_client import SocketIO

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
	socketIO.emit('player_input', {'position': 200, 'force': 2000, 'angle': 120})

socketIO.emit('connect_game', {'playerKey': player2Key, 'gameKey': gameKey})
socketIO.on('connect_game', connection_response)
socketIO.on('your_turn', coin_positions)
#socketIO.emit('player_input', {'position': 200, 'force': 2000, 'angle': 80})
socketIO.wait()

