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

def reflection_point(point1, point2, pocket):
	x1, y1 = point1[0], point1[1]
	x2, y2 = point2[0], point2[1]
	if pocket == 4:
		y = 25
		x = ((x1 * y) + (x2 * y) - (x1 * y2) - (x2 * y1)) / ((2 * y) - y1 - y2)
		point = (x, y)
	elif pocket == 2:
		y = 975
		x = ((x1 * y) + (x2 * y) - (x1 * y2) - (x2 * y1)) / ((2 * y) - y1 - y2)
		point = (x, y)
	elif pocket == 3 or pocket == 1:
		x = 975
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
	connected4 = []
	clean1 = clean_strikes(positions, pocket4_point, positions, 50)
	for coins in clean1:
		coins_x, coins_y = coins['x'], coins['y']
		coins_point = (coins_x, coins_y)
		print 'distance_between_points: ', distance_between_points(coins_point, pocket4_point)
		hitpt = hit_point(coins_point, pocket4_point, 4)
		hit_x, hit_y = hitpt[0], hitpt[1]
		for i in range(806, 194, -51):
			striker_y = 500
			striker_point = (striker_x, striker_y)
			strike_point = reflection_point(striker_point, hitpt, 4)
			distance = distance_between_points(striker_point, strike_point) + distance_between_points(strike_point, coins_point)
			force = distance * 6.9
			if force > 10000:
				force = 10000 
			print 'distance_travelled: ', distance
			strike_x, strike_y = strike_point[0], strike_point[1]
			path = True
			for coin in positions:
				if coin == coins:
					continue
				coin_x, coin_y = coin['x'], coin['y']
				if Point(coin_x, coin_y).intersects(LineString((striker_point, strike_point, hitpt)).buffer(55)):
					path = False
					break
			if path:
				coin_pocket = (hitpt, pocket4_point)
				coin_striker = (hitpt, strike_point)
				angle_striker_coin_pocket = ang(coin_pocket, coin_striker)
				position = striker_y
				slope = (striker_y - strike_y) / (striker_x - strike_x)
				angle = math.degrees(math.atan(slope)) + 90
				# force = 5000
				break
		if path:
			break
	print 'angle mutual: ', angle_striker_coin_pocket
	socketIO.emit('player_input', {'position': position, 'force': force, 'angle': angle})
	socketIO.on('player_input', emit_response)

socketIO.emit('connect_game', {'playerKey': player1Key, 'gameKey': gameKey})
socketIO.on('connect_game', connection_response)
socketIO.on('your_turn', coin_positions)
socketIO.wait()