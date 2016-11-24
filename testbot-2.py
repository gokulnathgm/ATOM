from socketIO_client import SocketIO
import random
import math
from shapely.geometry import *

socketIO = SocketIO('localhost', 4000)
print socketIO.connected

player1Key = 'p11'
player2Key = 'p12'
gameKey = '1'

def reflection_point(point1, point2):
	x1, y1 = point1[0], point1[1]
	x2, y2 = point2[0], point2[1]
	x = (((x1 * y2) + (x2 * y1)) / (y1 + y2))
	return (x, 0)

def emit_response(*args):
	print 'Emit response'
	print args

def connection_response(*args):
	print 'connection_response'
	print args

def coin_positions(*args):
	striker_x = 153.2258
	striker_y = 194

	pocket4_x = 967.7419
	pocket4_y = 967.7419
	pocket3_x = 32.2581
	pocket3_y = 967.7419
	pocket2_x = 967.7419
	pocket2_y = 32.2581
	pocket1_x = 32.2581
	pocket1_y = 32.2581

	pocket4_point = (pocket4_x, pocket4_y)
	pocket3_point = (pocket3_x, pocket3_y)
	pocket2_point = (pocket2_x, pocket2_y)
	pocket1_point = (pocket1_x, pocket1_y)
	striker_point = (striker_x, striker_y)
	positions = args[0]['position']
	black_coins = []
	white_coins = []
	red_coin = []
	for coin in positions:
		if coin['type'] == 'black':
			black_coins.append(coin)
		if coin['type'] == 'white':
			white_coins.append(coin)
		if coin['type'] == 'red':
			red_coin.append(coin)
	positions = []
	positions.extend(red_coin)
	positions.extend(white_coins)
	positions.extend(black_coins)
	args = positions[:]
	print 'args: ', args
	positions = []
	for coin in args:
		coin_x, coin_y = coin['x'], coin['y']
		if coin_x < 500 and coin_y > 194:
			positions.append(coin)
	print 'positions: ', positions
	for coin in positions:
		coin_x, coin_y = coin['x'], coin['y']
		coin_point = (coin_x, coin_y)
		strike_point = reflection_point(coin_point, pocket2_point)
		print 'strike_point', strike_point
		strike_x, strike_y = strike_point[0], strike_point[1]
		m = (coin_y - strike_y) / (coin_x - strike_x)
		int_y = m * (153.2258 - coin_x) + coin_y
		angle = math.degrees(math.atan(m))
		angle += 90
		int_x = 153.2258
		if int_y > 806.5416 or int_y < 193.5484:
			continue
		intersection_point = (int_x, int_y)
		print 'intersection point: ', intersection_point
		path = True
		for j in args:
			pos_x = j['x']
			pos_y = j['y']
			if pos_x < 153.2258 or j == coin:
				continue
			if Point(pos_x, pos_y).intersects(LineString((intersection_point, strike_point, pocket2_point)).buffer(55)):
				path = False
				break
		if path:
			position = int_y
			force = 9000
			break

	socketIO.emit('player_input', {'position': position, 'force': force, 'angle': angle})
	socketIO.on('player_input', emit_response)

socketIO.emit('connect_game', {'playerKey': player1Key, 'gameKey': gameKey})
socketIO.on('connect_game', connection_response)
socketIO.on('your_turn', coin_positions)
socketIO.wait()