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

def dot(vA, vB):
    return vA[0] * vB[0] + vA[1] * vB[1]

def ang(lineA, lineB):
    vA = [(lineA[0][0] - lineA[1][0]), (lineA[0][1] - lineA[1][1])]
    vB = [(lineB[0][0] - lineB[1][0]), (lineB[0][1] - lineB[1][1])]
    dot_prod = dot(vA, vB)
    magA = dot(vA, vA) ** 0.5
    magB = dot(vB, vB) ** 0.5
    print 'angle: ', dot_prod / magB / magA
    angle = math.acos(dot_prod / magB / magA)
    ang_deg = math.degrees(angle) % 360
    if ang_deg - 180 >= 0:
        return 360 - ang_deg
    else: 
        return ang_deg	

def clean_strikes(coins, destination_point, positions, radius_total):
	strike_through = []
	pocket_point = (destination_point[0], destination_point[1])
	for coin in coins:
		coin_x = coin['x']
		coin_y = coin['y']
		coin_point = (coin_x, coin_y)
		distance_coin_pocket = distance_between_points(coin_point, destination_point)
		path = True
		for coin_subset in positions:
			coin_subset_x = coin_subset['x']
			coin_subset_y = coin_subset['y']
			coin_subset_point = (coin_subset_x, coin_subset_y)
			distance_subset_coin_pocket = distance_between_points(coin_subset_point, destination_point)
			distance_between_coins = distance_between_points(coin_point, coin_subset_point)
			if(distance_coin_pocket > distance_between_coins and distance_coin_pocket > distance_subset_coin_pocket):
				if Point(coin_subset_x, coin_subset_y).intersects(LineString((coin_point,pocket_point)).buffer(radius_total)):
					path = False
					break
		if path:
			strike_through.append(coin)
	return strike_through

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
	strikes = []
	clean1 = clean_strikes(positions, pocket3_point, positions, 50)
	for coins in clean1:
		coins_x, coins_y = coins['x'], coins['y']
		coins_point = (coins_x, coins_y)
		intxn = hit_point(coins_point, pocket3_point, 3)
		print 'hitpt', intxn, coins
		intxn_x, intxn_y = intxn[0], intxn[1]
		for coin in positions:
			coin_x = coin['x']
			coin_y = coin['y']
			coin_point = (coin_x, coin_y)
			if coin == coins or coin_y > coins_y or intxn_x > coin_x:
				continue
			for i in range(194, 806, 51):
				strike = {}
				if i > coin_y:
					break
				striker_y = i
				striker_point = (striker_x, striker_y)
				hitpt = hit_point(coin_point, intxn, 3)
				path = True
				for j in positions:
					if j == coin or j == coins:
						continue
					pos_x = j['x']
					pos_y = j['y']
					if Point(pos_x, pos_y).intersects(LineString((striker_point, hitpt)).buffer(55)) or Point(pos_x, pos_y).intersects(LineString((hitpt, intxn)).buffer(50)):
						path = False
						break
				if path:
					slope = (striker_y - hitpt[1]) / (striker_x - hitpt[0])
					angle = math.degrees(math.atan(slope)) + 270
					coin_pocket = (hitpt, intxn)
					coin_striker = (hitpt, striker_point)
					angle_striker_coin_pocket = ang(coin_pocket, coin_striker)
					strike['angle'] = angle
					strike['position'] = i
					strike['angle_mutual'] = angle_striker_coin_pocket
					strike['type'] = coins['type']
					strike['force'] = 5000
					strike['function'] = 'pocket3_connected'
					strike['id'] = coins['id']
					strikes.append(strike)
	print 'strikes', strikes
	position = strikes[0]['position']
	angle = strikes[0]['angle']
	socketIO.emit('player_input', {'position': position, 'force': 5000, 'angle': angle})
	socketIO.on('player_input', emit_response)

socketIO.emit('connect_game', {'playerKey': player1Key, 'gameKey': gameKey})
socketIO.on('connect_game', connection_response)
socketIO.on('your_turn', coin_positions)
socketIO.wait()