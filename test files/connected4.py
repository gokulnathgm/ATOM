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
	connected4 = []
	pocket4_results = []
	clean1 = clean_strikes(positions, pocket4_point, positions, 50)
	for coins in clean1:
		coins_x, coins_y = coins['x'], coins['y']
		coins_point = (coins_x, coins_y)
		intxn = hit_point(coins_point, pocket4_point, 4)
		intxn_x, intxn_y = intxn[0], intxn[1]
		print 'hitpt: ', intxn, coins
		for coin in positions:
			red_strikes = {}
			coin_x = coin['x']
			coin_y = coin['y']
			coin_point = (coin_x, coin_y)
			if coin_x < 153.2258 + 55 or coin == coins:
				continue
			m = (coin_y - intxn_y) / (coin_x - intxn_x)
			int_y = m * (153.2258 - coin_x) + coin_y
			angle = math.degrees(math.atan(m))
			angle += 90
			int_x = 153.2258
			if int_y > 806.5416 or int_y < 193.5484:
				continue
			intersection_point = (int_x, int_y)
			coin_pocket = (intxn, pocket4_point)
			coin_striker = (intxn,coin_point)
			angle_striker_coin_pocket = ang(coin_pocket, coin_striker)
			path = True
			if angle_striker_coin_pocket < 150:
				continue
			for j in positions:
				if j == coin or j == coins:
					continue
				pos_x = j['x']
				pos_y = j['y']
				if Point(pos_x, pos_y).intersects(LineString((coin_point,intersection_point)).buffer(55)):
					path = False
					break
			if path:
				red_hit = True
				red_strikes['angle'] = angle
				red_strikes['position'] = float(int_y)
				red_strikes['angle_mutual'] = angle_striker_coin_pocket
				red_strikes['type'] = coin['type']
				red_strikes['force'] = 5500
				pocket4_results.append(red_strikes)
	print pocket4_results
	position = pocket4_results[0]['position']
	angle = pocket4_results[0]['angle']
	socketIO.emit('player_input', {'position': position, 'force': 5500, 'angle': angle})
	socketIO.on('player_input', emit_response)

socketIO.emit('connect_game', {'playerKey': player1Key, 'gameKey': gameKey})
socketIO.on('connect_game', connection_response)
socketIO.on('your_turn', coin_positions)
socketIO.wait()