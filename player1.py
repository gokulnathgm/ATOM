from socketIO_client import SocketIO
from sympy.geometry import *
from sympy import sympify
import math
import multiprocessing as mp
from multiprocessing import Manager
import sys, select
import time
from shapely.geometry import *

# socketIO = SocketIO('10.7.90.8', 4000)
socketIO = SocketIO('localhost', 4000)
print socketIO.connected

# player1Key = 'T8uhv56xvs'
# player2Key = 'GSwwserRd2'
# gameKey = '9lVRq6Py7a3Vl1I0c4Fm'

player1Key = 'p11'
player2Key = 'p12'
gameKey = '1'

# player1Key = 'Jkuy6wsxDa'
# player2Key = 'GSwwserRd2'
# gameKey = 'Has4RtgBnhj3WsaQw3Lo'


first_strike = True
set_strike_first = False

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

def distance_between_points(point1, point2):
	x1, y1 = point1[0], point1[1]
	x2, y2 = point2[0], point2[1]
	distance = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
	return distance

def clean_strikes(coins, destination_point, positions, radius_total, between):
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
			if between == 0:
				if destination_point === pocket4_point:
					if coin_subset_x < coin_x - 25 or coin_subset_y < coin_y - 25:
						continue
				elif destination_point === pocket2_point:
					if coin_subset_x < coin_x - 25 or coin_subset_y > coin_y + 25:
						continue
				elif destination_point === pocket3_point:
					if coin_subset_x > coin_x + 25 or coin_subset_y < coin_y - 25:
						continue	
				else: 
					if coin_subset_x > coin_x + 25 or coin_subset_y > coin_y + 25:
						continue
			elif between == 4:
				if coin_subset_x > coin_x + 25 or coin_subset_y > coin_y + 25:
					continue	
			elif between == 2:
				if coin_subset_x > coin_x + 25 or coin_subset_y < coin_y - 25:
					continue
			elif between == 3:
				if coin_subset_x < coin_x - 25 or coin_subset_y > coin_y + 25:
					continue
			else:
				if coin_subset_x < coin_x - 25 or coin_subset_y < coin_y - 25:
					continue														
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

def through_shot(coins, positions, pocket):
	through_coins = []
	strike_line = Line((153.2258, 193.5484),(153.2258, 806.4516))
	for coin in coins:
		coin_x = coin['x']
		coin_y = coin['y']
		coin_point = (coin_x, coin_y)
		coin_pocket = Line(coin_point, pocket)
		intersection_point = strike_line.intersection(coin_pocket)
		int_x = intersection_point[0][0]
		int_y = intersection_point[0][1]
		if int_y > 806.5416 or int_y < 153.2258:
			continue
		intersection_point = (int_x, int_y)
		path = True
		for j in positions:
			pos_x = j['x']
			pos_y = j['y']
			if pos_x >= coin_x:
				continue
			if Point(pos_x, pos_y).intersects(LineString((coin_point,intersection_point)).buffer(55)):
				path = False
				break
		if path:
			through_coins.append(coin);
	return through_coins

def emit_response(*args):
	print 'Emit response'
	print args, '\n'

def connection_response(*args):
	print 'connection_response'
	print args, '\n'

def coin_positions(*args):
	start_time = time.time()
	print args
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

	manager = Manager()
	return_dict = manager.dict()
	global first_strike
	global set_strike_first
	# first_strike = False
	if first_strike:
		first_strike = False
		angle = 90
		position = 500
		force = 10000
	else:
		q = mp.Queue()
		job1 = mp.Process(target=coin_positions4, args=(positions, return_dict))
		job2 = mp.Process(target=coin_positions2, args=(positions, return_dict))
		job1.start()
		job2.start()
		job1.join()
		job2.join()

		print 'results4', return_dict['pocket4'], '\n' 
		print 'results2', return_dict['pocket2'], '\n'

		result = return_dict['pocket4']
		result.extend(return_dict['pocket2'])

		black = []
		white = []
		red = []
		for coin in result:
			if coin['type'] == 'black':
				black.append(coin)
	
			if coin['type'] == 'white':
				white.append(coin)
			
			if coin['type'] == 'red':
				red.append(coin)

		red = sorted(red, key=lambda k: k['angle_mutual'], reverse=True) 
		white = sorted(white, key=lambda k: k['angle_mutual'], reverse=True) 
		black = sorted(black, key=lambda k: k['angle_mutual'], reverse=True) 

		if red:
			angle = red[0]['angle']
			force = red[0]['force']
			position = red[0]['position']
			print red[0]
		elif white:
			angle = white[0]['angle']
			force = white[0]['force']
			position = white[0]['position']
			print white[0]
		elif black:
			angle = black[0]['angle']
			force = black[0]['force']
			position = black[0]['position']
			print black[0]

		if not result:
			striker_positions = []
			for i in range(194,806,20):
				valid_position = True
				for j in positions:
					j_x = j['x']
					j_y = j['y']
					if (j_x > 99 and j_x < 209) and (j_y > i - 55 and j_y < i + 55):
						valid_position = False
						break
				if valid_position:
					striker_positions.append(i)
			striker_y = striker_positions[len(striker_positions) / 2]
			striker_point = (striker_x, striker_y)
			coin_x = positions[0]['x']
			coin_y = positions[0]['y']
			coin = (coin_x, coin_y)
			line_coin_striker = Line(coin, striker_point)
			slope_coin_striker = line_coin_striker.slope
			angle = math.degrees(math.atan(slope_coin_striker))
			force = 8000
			position = striker_y
			if coin_x < striker_x:
				angle += 270
			else:
				angle += 90

	print("---------- %s seconds -----------" % (time.time() - start_time))
	print {'position': position, 'force': force, 'angle': angle}, '\n'
	socketIO.emit('player_input', {'position': position, 'force': force, 'angle': angle})

def coin_positions4(args, return_dict):
	print 'Aiming for pocket4...' ,'\n'
	pocket4_results = []
	positions = args
	
	strike_through_pocket = clean_strikes(positions, pocket4_point, positions, 50, 0)
	print 'clean1: ', strike_through_pocket, '\n'

	if strike_through_pocket:
		through_coins = through_shot(strike_through_pocket, args, pocket4_point)
		print '\nthrough coins: ', through_coins, '\n'

	striker_pos = [194, 806, 294, 394, 494, 594, 694]
	for i in striker_pos:
		striker_ok = True	
		striker_y = i
		striker_point = (striker_x, striker_y)

		for j in args:
			x = j['x']
			y = j['y']
			if (x > 99 and x < 209) and (y > striker_y - 55 and y < striker_y + 55):
				striker_ok = False
				break
		if not striker_ok:
			continue

		strike_through_pocket_modified = []
		for coin in strike_through_pocket:
			coin_x = coin['x']
			coin_y = coin['y']
			if coin_y < 194 + 50 or coin_x < 153 + 50:
				continue
			coin_point = (coin_x, coin_y)
			circle = Circle(coin_point, 55)
			line_coin_pocket = Line(coin_point, pocket4_point)
			intersection_points = circle.intersection(line_coin_pocket)
			intersection_point_x = float(intersection_points[0][0])
			intersection_point_y = float(intersection_points[0][1])
			point = {'x': intersection_point_x, 'y': intersection_point_y, 'type': coin['type'], 'id': coin['id']}
			strike_through_pocket_modified.append(point)

		strike_through_striker = clean_strikes(strike_through_pocket_modified, striker_point, positions, 55, 4)
		print 'clean2: ', strike_through_striker, '\n'

		striked = False
		if strike_through_striker:
			for coin in strike_through_striker:
				coin_x = coin['x']
				coin_y = coin['y']
				coin_pocket = ((coin_x, coin_y), (1000, 1000))
				coin_striker = ((coin_x, coin_y),(striker_x, striker_y))
				angle_striker_coin_pocket = ang(coin_pocket, coin_striker)
				if angle_striker_coin_pocket < 140:
					continue
				coin_point = (coin_x, coin_y)
				strike_line = Line(coin_point, striker_point)
				slope = strike_line.slope
				angle = math.degrees(math.atan(slope))

				distance_striker_to_coin = math.hypot(coin_x - striker_x, coin_y - striker_y)
				distance_coin_to_pocket = math.hypot(pocket4_x - coin_x, pocket4_y - coin_y)
				total_distance = distance_striker_to_coin + distance_coin_to_pocket
				if angle_striker_coin_pocket >= 170:
				 	force = total_distance * 4.7
				elif angle_striker_coin_pocket < 170 and angle_striker_coin_pocket >= 150:
				 	force = total_distance * 5.1
				else:
				 	force = total_distance * 5.3
				if total_distance < 800:
				 	force =	total_distance * 5

				angle += 90
				strike = {'angle': angle, 'force': force, 'position': i, 'angle_mutual': angle_striker_coin_pocket, 'type': coin['type']}
				pocket4_results.append(strike)
				striked = True
				break
			if striked:
				break
	return_dict['pocket4'] = pocket4_results

def coin_positions2(args, return_dict):
	print 'Aiming for pocket2...' ,'\n'
	positions = args
	pocket2_results = []

	strike_through_pocket = clean_strikes(positions, pocket2_point, positions, 50, 0)
	print 'clean1: ', strike_through_pocket, '\n'

	striker_pos = [806, 194, 706, 606, 506, 406, 306]
	for i in striker_pos:
		striker_ok = True	
		striker_y = i
		striker_point = (striker_x, striker_y)

		for j in args:
			x = j['x']
			y = j['y']
			if (x > 99 and x < 209) and (y > striker_y - 55 and y < striker_y + 55):
				striker_ok = False
				break
		if not striker_ok:
			continue

		strike_through_pocket_modified = []
		for coin in strike_through_pocket:
			coin_x = coin['x']
			coin_y = coin['y']
			if coin_y > 806 - 50 or coin_x < 153 + 50:
				continue
			coin_point = (coin_x, coin_y)
			circle = Circle(coin_point, 55)
			line_coin_pocket = Line(coin_point, pocket2_point)
			intersection_points = circle.intersection(line_coin_pocket)
			intersection_point_x = float(intersection_points[0][0])
			intersection_point_y = float(intersection_points[0][1])
			point = {'x': intersection_point_x, 'y': intersection_point_y, 'x1': coin_x, 'y1': coin_y, 'type': coin['type'], 'id': coin['id']}
			strike_through_pocket_modified.append(point)

		strike_through_striker = clean_strikes(strike_through_pocket_modified, striker_point, positions, 55, 2)
		print 'clean2: ', strike_through_striker, '\n'

		striked = False
		if strike_through_striker:
			for coin in strike_through_striker:
				coin_x = coin['x']
				coin_y = coin['y']
				coin_pocket = ((coin_x, coin_y), (1000, 0))
				coin_striker = ((coin_x, coin_y),(striker_x, striker_y))
				angle_striker_coin_pocket = ang(coin_pocket, coin_striker)
				if angle_striker_coin_pocket < 140:
					continue
				coin_point = (coin_x, coin_y)
				strike_line = Line(coin_point, striker_point)
				slope = strike_line.slope
				angle = math.degrees(math.atan(slope))

				distance_striker_to_coin = math.hypot(coin_x - striker_x, coin_y - striker_y)
				distance_coin_to_pocket = math.hypot(pocket2_x - coin_x, pocket2_y - coin_y)
				total_distance = distance_striker_to_coin + distance_coin_to_pocket
				if angle_striker_coin_pocket >= 170:
				 	force = total_distance * 4.7
				elif angle_striker_coin_pocket < 170 and angle_striker_coin_pocket >= 150:
				 	force = total_distance * 5.1
				else:
				 	force = total_distance * 5.3
				if total_distance < 800:
				 	force =	total_distance * 5
				
				angle += 90
				strike = {'angle': angle, 'force': force, 'position': i, 'angle_mutual': angle_striker_coin_pocket, 'type': coin['type']}
				pocket2_results.append(strike)
				striked = True
				break
			if striked:
				break
	return_dict['pocket2'] = pocket2_results

socketIO.on('player_input', emit_response)
socketIO.emit('connect_game', {'playerKey': player1Key, 'gameKey': gameKey})
socketIO.on('connect_game', connection_response)
socketIO.on('your_turn', coin_positions)
socketIO.wait()
