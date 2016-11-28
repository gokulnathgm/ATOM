from socketIO_client import SocketIO
import random
import math
from shapely.geometry import *

socketIO = SocketIO('localhost', 4000)
print socketIO.connected

player1Key = 'p11'
player2Key = 'p12'
gameKey = '1'

def hit_point(coin_point, pocket_point, pocket):
	coin_x, coin_y = coin_point[0], coin_point[1]
	pocket_x, pocket_y = pocket_point[0], pocket_point[1]
	m = (pocket_y - coin_y) / (pocket_x - coin_x)
	if coin_x < pocket_x:
		int_x = coin_x - (55 / math.sqrt(1 + m * m))
	elif coin_x > pocket_x:
		int_x = coin_x + (55 / math.sqrt(1 + m * m))
	elif pocket == 2 or pocket == 4:
		int_x = coin_x - (55 / math.sqrt(1 + m * m))
	else:
		int_x = coin_x + (55 / math.sqrt(1 + m * m))
	int_y = coin_y +  (m * (int_x - coin_x))
	intxn = (int_x, int_y)
	return intxn

def reflection_point(point1, point2, pocket):
	x1, y1 = point1[0], point1[1]
	x2, y2 = point2[0], point2[1]
	if pocket == 4:
		y = 30
		x = ((x1 * y) + (x2 * y) - (x1 * y2) - (x2 * y1)) / ((2 * y) - y1 - y2)
		point = (x, y)
	elif pocket == 2:
		y = 970
		x = ((x1 * y) + (x2 * y) - (x1 * y2) - (x2 * y1)) / ((2 * y) - y1 - y2)
		point = (x, y)
	elif pocket == 3 or pocket == 1:
		x = 970
		y = ((x * y1) + (x * y2) - (x1 * y2) - (x2 * y1)) / ((2 * x) - x1 - x2)
		point = (x, y)
	return point	

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
	# args = positions[:]
	# print 'args: ', args
	# positions = []
	# for coin in args:
	# 	coin_x, coin_y = coin['x'], coin['y']
	# 	if coin_y < 806:
	# 		positions.append(coin)
	# print 'positions: ', positions
	for coin in positions:
		coin_x, coin_y = coin['x'], coin['y']
		coin_point = (coin_x, coin_y)
		hitpt = hit_point(coin_point, pocket4_point, 4)
		print 'hitpt: ', hitpt
		striker_y = 250
		striker_point = (striker_x, striker_y)
		strike_point = reflection_point(hitpt, striker_point, 4)
		print 'strike_point', strike_point, coin
		strike_x, strike_y = strike_point[0], strike_point[1]
		m = (striker_y - strike_y) / (striker_x - strike_x)
		int_y = m * (153.2258 - striker_x) + striker_y
		angle = math.degrees(math.atan(m))
		angle += 90
		int_x = 153.2258
		if int_y > 806.5416 or int_y < 193.5484:
			continue
		position = striker_y
		force = 9000
		break

	socketIO.emit('player_input', {'position': position, 'force': force, 'angle': angle})
	socketIO.on('player_input', emit_response)

socketIO.emit('connect_game', {'playerKey': player1Key, 'gameKey': gameKey})
socketIO.on('connect_game', connection_response)
socketIO.on('your_turn', coin_positions)
socketIO.wait()