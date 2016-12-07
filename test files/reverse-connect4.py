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
	print 'clean1: ', clean1
	for coins in clean1:
		coins_x, coins_y = coins['x'], coins['y']
		coins_point = (coins_x, coins_y)
		hitpt = hit_point(coins_point, pocket4_point, 4)
		hit_x, hit_y = hitpt[0], hitpt[1]
		print 'hitpt: ', hitpt, coins
		positions_new = positions[:]
		positions_new.remove(coins)
		clean2 = clean_strikes(positions_new, hitpt, positions_new, 50)
		modified = []
		print 'clean2: ', clean2
		for pos in clean2:#strike through pocket
			positions_new.remove(pos)
			pos_x = pos['x']
			pos_y = pos['y']
			if pos_y < 194 + 50 or pos_x < 153 + 50:
				continue
			pos_point = (pos_x, pos_y)
			intersection_point = hit_point(pos_point, hitpt, 4)
			intersection_point_x = intersection_point[0]
			intersection_point_y = intersection_point[1]
			point = {'x': intersection_point_x, 'y': intersection_point_y, 'type': pos['type'], 'id': pos['id']}
			modified.append(point)
		print 'modified: ', modified
		print 'positions_new: ', positions_new
		for i in range(194, 806, 51):
			striker_y = i
			striker_point = (striker_x, striker_y)
			for coin in modified:
				coin_x, coin_y = coin['x'], coin['y']
				coin_point = (coin_x, coin_y)
				for j in positions_new:
					pos_x = j['x']
					pos_y = j['y']
					if Point(pos_x, pos_y).intersects(LineString((striker_point,coin_point)).buffer(55)) or Point(pos_x, pos_y).intersects(LineString((coin_point, hitpt)).buffer(50)):
						break
				coin_pocket = ((coin_x, coin_y), pocket4_point)
				coin_striker = ((coin_x, coin_y),(striker_x, striker_y))
				angle_striker_coin_pocket = ang(coin_pocket, coin_striker)
				slope = (coin_y - striker_y) / (coin_x - striker_x)
				angle = math.degrees(math.atan(slope))
				force = 6000
				angle += 90
				strike = {'angle': angle, 'angle_mutual': angle_striker_coin_pocket, 'force': force, 'position': i, 'type': coin['type'], 'id': coin['id'], 'hitpt:': hitpt}
				connected4.append(strike)
	print 'connected4', connected4
	result = sorted(connected4, key=lambda k: k['angle_mutual'], reverse=True) 
			# strike_through = clean_strikes(modified, hitpt, positions, 55)
			# print 'strike_through: ', strike_through
			# if strike_through:
			# 	for coin in strike_through:
			# 		coin_x = coin['x']
			# 		coin_y = coin['y']
			# 		coin_pocket = ((coin_x, coin_y), pocket4_point)
			# 		coin_striker = ((coin_x, coin_y),(striker_x, striker_y))
			# 		angle_striker_coin_pocket = ang(coin_pocket, coin_striker)
			# 		if angle_striker_coin_pocket < 145:
			# 			continue
			# 		coin_point = (coin_x, coin_y)
			# 		slope = (coin_y - striker_y) / (coin_x - striker_x)
			# 		angle = math.degrees(math.atan(slope))
			# 		distance_striker_to_coin = math.hypot(coin_x - striker_x, coin_y - striker_y)
			# 		distance_coin_to_pocket = math.hypot(pocket4_x - coin_x, pocket4_y - coin_y)
			# 		total_distance = distance_striker_to_coin + distance_coin_to_pocket
			# 		if angle_striker_coin_pocket >= 170:
			# 		 	force = total_distance * 4.7
			# 		elif angle_striker_coin_pocket < 170 and angle_striker_coin_pocket >= 150:
			# 		 	force = total_distance * 5.1
			# 		else:
			# 		 	force = total_distance * 5.4
			# 		if total_distance < 800:
			# 		 	force =	total_distance * 5
	position = result[0]['position']
	angle = result[0]['angle']
	socketIO.emit('player_input', {'position': position, 'force': 6000, 'angle': angle})
	socketIO.on('player_input', emit_response)

socketIO.emit('connect_game', {'playerKey': player1Key, 'gameKey': gameKey})
socketIO.on('connect_game', connection_response)
socketIO.on('your_turn', coin_positions)
socketIO.wait()