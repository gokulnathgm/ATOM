from socketIO_client import SocketIO
import math
import multiprocessing as mp
from multiprocessing import Manager
import time
from shapely.geometry import *

socketIO = SocketIO('10.7.90.8', 4000)
print socketIO.connected

# player1Key = 'T8uhv56xvs'
# player2Key = 'GSwwserRd2'
# gameKey = '9lVRq6Py7a3Vl1I0c4Fm'

# socketIO = SocketIO('localhost', 4000)
# print socketIO.connected

# player1Key = 'p11'
# player2Key = 'p12'
# gameKey = '1'

player1Key = 'T8uhv56xvs'
player2Key = 'NlopqsKd4V'
gameKey = 'Bd4RtiK6Tqas2mKnhvB6'

striker_x = 846.7742
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

def hit_point(coin_point, pocket_point, pocket):
	coin_x, coin_y = coin_point[0], coin_point[1]
	pocket_x, pocket_y = pocket_point[0], pocket_point[1]
	m = (pocket_y - coin_y) / (pocket_x - coin_x)
	if coin_x > pocket_x:
		int_x = coin_x + (55 / math.sqrt(1 + m * m))
	elif coin_x < pocket_x:
		int_x = coin_x - (55 / math.sqrt(1 + m * m))
	elif pocket == 2 or pocket == 4:
		int_x = coin_x - (55 / math.sqrt(1 + m * m))
	else:
		int_x = coin_x + (55 / math.sqrt(1 + m * m))
	int_y = coin_y +  (m * (int_x - coin_x))
	intxn = (int_x, int_y)
	return intxn

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

	q = mp.Queue()
	job1 = mp.Process(target=coin_positions3, args=(positions, return_dict))
	job2 = mp.Process(target=coin_positions1, args=(positions, return_dict))
	job3 = mp.Process(target=coin_positions4, args=(positions, return_dict))
	job4 = mp.Process(target=coin_positions2, args=(positions, return_dict))
	job1.start()
	job2.start()
	job3.start()
	job4.start()
	job1.join()
	job2.join()
	job3.join()
	job4.join()

	print '\nresults3', return_dict['pocket3'], '\n' 
	print '\nresults1', return_dict['pocket1'], '\n'
	print '\nresults4', return_dict['pocket4'], '\n'
	print '\nresults2', return_dict['pocket2'], '\n'

	result = return_dict['pocket3']
	result.extend(return_dict['pocket1'])
	result.extend(return_dict['pocket4'])
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
		print 'struck coin: ', red[0]
	elif white:
		angle = white[0]['angle']
		force = white[0]['force']
		position = white[0]['position']
		print 'struck coin: ', white[0]
	elif black:
		angle = black[0]['angle']
		force = black[0]['force']
		position = black[0]['position']
		print 'struck coin: ', black[0]
		
	if not result:
		striker_positions = []
		for i in range(194,806,20):
			valid_position = True
			for j in positions:
				j_x = j['x']
				j_y = j['y']
				if (j_x > 792 and j_x < 902) and (j_y > i - 55 and j_y < i + 55):
					valid_position = False
					break
			if valid_position:
				striker_positions.append(i)
			
		coin_x = positions[0]['x']
		coin_y = positions[0]['y']
		coin_point = (coin_x, coin_y)
		if coin_y < 153:
			striker_y = striker_positions[0]
			intersection_point = hit_point(coin_point, pocket2_point, 2)
			int_x, int_y = intersection_point[0], intersection_point[1]
			mid_y = (int_y + striker_y) / 2
			mid_x = 0
			slope = (mid_y - striker_y) / (mid_x - striker_x)
			angle = math.degrees(math.atan(slope))
			angle += 90
			position = striker_y
			force = 10000
		elif coin_y > 847:
			striker_y = striker_positions[len(striker_positions) - 1]
			intersection_point = hit_point(coin_point, pocket4_point, 4)
			int_x, int_y = intersection_point[0], intersection_point[1]
			mid_y = (int_y + striker_y) / 2
			mid_x = 0
			slope = (mid_y - striker_y) / (mid_x - striker_x)
			angle = math.degrees(math.atan(slope))
			angle += 90
			position = striker_y
			force = 10000
		else:
			if coin_y > 500:
				striker_y = striker_positions[0]
				pocket_point = pocket3_point
				pocket = 3
			else:
				striker_y = striker_positions[len(striker_positions) - 1]
				pocket_point = pocket1_point
				pocket = 1
		
			striker_point = (striker_x, striker_y)
			intersection_point = hit_point(coin_point, pocket_point, pocket)
			intersection_point_x = intersection_point[0]
			intersection_point_y = intersection_point[1]
			slope = (intersection_point_y - striker_y) / (intersection_point_x - striker_x)
			angle = math.degrees(math.atan(slope))
			force = 1500
			position = striker_y
			angle += 90

	print("---------- %s seconds -----------" % (time.time() - start_time))
	print {'position': position, 'force': force, 'angle': angle}, '\n'
	socketIO.emit('player_input', {'position': position, 'force': force, 'angle': angle})



def coin_positions3(args, return_dict):
	print 'Aiming for pocket3...' ,'\n'
	pocket3_results = []
	positions = args
	
	strike_through_pocket = clean_strikes(positions, pocket3_point, positions, 50)
	print 'clean13: ', strike_through_pocket, '\n'

	through_coin = {}
	if strike_through_pocket:
		for coin in strike_through_pocket:
			coin_x = coin['x']
			coin_y = coin['y']
			if coin_x > 846.7742 - 55:
				continue
			coin_point = (coin_x, coin_y)
			m = (coin_y - pocket3_y) / (coin_x - pocket3_x)
			int_y = m * (846.7742 - coin_x) + coin_y
			angle = math.degrees(math.atan(m))
			angle += 90
			int_x = 846.7742
			if int_y > 806.5416 or int_y < 193.5484:
				continue
			intersection_point = (int_x, int_y)
			path = True
			for j in positions:
				pos_x = j['x']
				pos_y = j['y']
				if (pos_x > 792 and pos_x < 902) and (pos_y > int_y - 55 and pos_y < int_y + 55):
					path = False
					break
				if pos_x <= coin_x:
					continue
				if Point(pos_x, pos_y).intersects(LineString((coin_point,intersection_point)).buffer(55)):
					path = False
					break
			if path:
				through_coin['angle'] = angle
				through_coin['position'] = float(int_y)
				through_coin['angle_mutual'] = 180
				through_coin['type'] = coin['type']
				through_coin['force'] = 5000
				pocket3_results.append(through_coin)
				break

		if 'red' not in through_coin.values() and strike_through_pocket[0]['type'] == 'red':
			coin_point = (strike_through_pocket[0]['x'], strike_through_pocket[0]['y'])
			intersection_point = hit_point(coin_point, pocket3_point, 3)
			intersection_point_x = intersection_point[0]
			intersection_point_y = intersection_point[1]
			intxy = intersection_point
			striker_positions = []
			red_hit = False
			for i in range(194,806,10):
				valid_position = True
				valid_strike = True
				red_strikes = {}
				striker_point = (striker_x, i)
				for j in positions:
					j_x = j['x']
					j_y = j['y']
					if (j_x > 792 and j_x < 902) and (j_y > i - 55 and j_y < i + 55):
						valid_position = False
					if valid_position and valid_strike:
						if j['type'] == 'red':
							continue
						if Point(j_x, j_y).intersects(LineString((striker_point, intersection_point, pocket3_point)).buffer(55)):
							valid_strike = False	
					if not valid_position or not valid_strike:
						break
				if valid_position and valid_strike:
					coin_pocket = (intersection_point, pocket3_point)
					coin_striker = (intersection_point,striker_point)
					angle_striker_coin_pocket = ang(coin_pocket, coin_striker)
					if angle_striker_coin_pocket > 140:
						red_hit = True
						slope = (intersection_point_y - i) / (intersection_point_x - striker_x)
						angle = math.degrees(math.atan(slope))
						angle += 90
						red_strikes['angle'] = angle
						red_strikes['position'] = i
						red_strikes['angle_mutual'] = angle_striker_coin_pocket
						red_strikes['type'] = 'red'
						red_strikes['force'] = 5200
						pocket3_results.append(red_strikes)

			if not red_hit:
				print '...................connected shot3 ..................'
				red_coin_x = strike_through_pocket[0]['x']
				red_coin_y = strike_through_pocket[0]['y']
				red_coin = (red_coin_x, red_coin_y)
				intxn = hit_point(red_coin, pocket3_point, 3)
				intxn_x, intxn_y = intxn[0], intxn[1]
				for coin in positions:
					red_strikes = {}
					coin_x = coin['x']
					coin_y = coin['y']
					coin_point = (coin_x, coin_y)
					if coin_x > 846.7742 - 55 or coin['type'] == 'red':
						continue
					m = (coin_y - intxn_y) / (coin_x - intxn_x)
					int_y = m * (846.7742 - coin_x) + coin_y
					angle = math.degrees(math.atan(m))
					angle += 90
					int_x = 846.7742
					if int_y > 806.5416 or int_y < 193.5484:
						continue
					intersection_point = (int_x, int_y)
					coin_pocket = (intxn, pocket3_point)
					coin_striker = (intxn,coin_point)
					angle_striker_coin_pocket = ang(coin_pocket, coin_striker)
					path = True
					if angle_striker_coin_pocket < 150:
						continue
					for j in positions:
						if j == coin or j['type'] == 'red':
							continue
						pos_x = j['x']
						pos_y = j['y']
						if (pos_x > 792 and pos_x < 902) and (pos_y > int_y - 55 and pos_y < int_y + 55):
							path = False
							break
						if pos_x <= coin_x:
							continue
						if Point(pos_x, pos_y).intersects(LineString((coin_point,intersection_point)).buffer(55)):
							path = False
							break
					if path:
						red_hit = True
						red_strikes['angle'] = angle
						red_strikes['position'] = float(int_y)
						red_strikes['angle_mutual'] = angle_striker_coin_pocket
						red_strikes['type'] = 'red'
						red_strikes['force'] = 5500
						pocket3_results.append(red_strikes)

			if not red_hit:
				intersection_point = intxy
				intersection_point_x = intxy[0]
				intersection_point_y = intxy[1]
				red_strikes = {}
				striker_y = intxy[1]
				if intersection_point_y >= 450:
					mid_y = 0
					mid_x = (intersection_point_x + striker_x) / 2
					mid_point = (mid_x, mid_y)
					striker_point = (striker_x, striker_y)
					striker = (striker_x, coin_point[1])
					path = True
					for j in positions:
						pos_x = j['x']
						pos_y = j['y']
						if (pos_x > 792 and pos_x < 902) and (pos_y > striker_y - 55 and striker_y < int_y + 55):
							path = False
							break
						if Point(pos_x, pos_y).intersects(LineString((striker, mid_point, intersection_point)).buffer(55)):
							path = False
							break
					if path:
						slope = (mid_y - striker_y) / (mid_x - striker_x)
						angle = math.degrees(math.atan(slope))
						angle += 90
						red_strikes['angle'] = angle
						red_strikes['position'] = strike_through_pocket[0]['y']
						red_strikes['angle_mutual'] = 180
						red_strikes['type'] = 'red'
						red_strikes['force'] = 8500
						pocket3_results.append(red_strikes)

	# striker_pos = [194, 806, 294, 394, 494, 594, 694]
	for i in range(194, 806, 50):
		striker_ok = True	
		striker_y = i
		striker_point = (striker_x, striker_y)

		for j in args:
			if j['type'] == 'stricker':
				continue
			x = j['x']
			y = j['y']
			if (x > 792 and x < 902) and (y > striker_y - 55 and y < striker_y + 55):
				striker_ok = False
				break
		if not striker_ok:
			continue

		strike_through_pocket_modified = []
		for coin in strike_through_pocket:
			coin_x = coin['x']
			coin_y = coin['y']
			if coin_y < 194 + 50 or coin_x > 846 - 50:
				continue
			coin_point = (coin_x, coin_y)
			intersection_point = hit_point(coin_point, pocket3_point, 3)
			intersection_point_x = intersection_point[0]
			intersection_point_y = intersection_point[1]
			point = {'x': intersection_point_x, 'y': intersection_point_y, 'type': coin['type'], 'id': coin['id']}
			strike_through_pocket_modified.append(point)

		strike_through_striker = clean_strikes(strike_through_pocket_modified, striker_point, positions, 55)

		striked = False
		if strike_through_striker:
			for coin in strike_through_striker:
				coin_x = coin['x']
				coin_y = coin['y']
				coin_pocket = ((coin_x, coin_y), pocket3_point)
				coin_striker = ((coin_x, coin_y),(striker_x, striker_y))
				angle_striker_coin_pocket = ang(coin_pocket, coin_striker)
				if angle_striker_coin_pocket < 145:
					continue
				coin_point = (coin_x, coin_y)
				slope = (coin_y - striker_y) / (coin_x - striker_x)
				angle = math.degrees(math.atan(slope))
				distance_striker_to_coin = math.hypot(coin_x - striker_x, coin_y - striker_y)
				distance_coin_to_pocket = math.hypot(pocket3_x - coin_x, pocket3_y - coin_y)
				total_distance = distance_striker_to_coin + distance_coin_to_pocket
				if angle_striker_coin_pocket >= 170:
				 	force = total_distance * 4.7
				elif angle_striker_coin_pocket < 170 and angle_striker_coin_pocket >= 150:
				 	force = total_distance * 5.1
				else:
				 	force = total_distance * 5.4
				if total_distance < 800:
				 	force =	total_distance * 5

				angle += 90
				strike = {'angle': angle, 'force': force, 'position': i, 'angle_mutual': angle_striker_coin_pocket, 'type': coin['type']}
				pocket3_results.append(strike)
			# 	striked = True
			# 	break
			# if striked:
			# 	break
	return_dict['pocket3'] = pocket3_results


def coin_positions1(args, return_dict):
	print 'Aiming for pocket1...' ,'\n'
	pocket1_results = []
	positions = args

	strike_through_pocket = clean_strikes(positions, pocket1_point, positions, 50)
	print 'clean11: ', strike_through_pocket, '\n'

	through_coin = {}
	if strike_through_pocket:
		for coin in strike_through_pocket:
			coin_x = coin['x']
			coin_y = coin['y']
			if coin_x > 846.7742 - 55:
				continue
			coin_point = (coin_x, coin_y)
			m = (coin_y - pocket1_y) / (coin_x - pocket1_x)
			int_y = m * (846.7742 - coin_x) + coin_y
			angle = math.degrees(math.atan(m))
			angle += 90
			int_x = 846.7742
			if int_y > 806.5416 or int_y < 153.2258:
				continue
			intersection_point = (int_x, int_y)
			path = True
			for j in positions:
				pos_x = j['x']
				pos_y = j['y']
				if (pos_x > 792 and pos_x < 902) and (pos_y > int_y - 55 and pos_y < int_y + 55):
					path = False
					break
				if pos_x <= coin_x:
					continue
				if Point(pos_x, pos_y).intersects(LineString((coin_point,intersection_point)).buffer(55)):
					path = False
					break
			if path:
				through_coin['angle'] = angle
				through_coin['position'] = float(int_y)
				through_coin['angle_mutual'] = 180
				through_coin['type'] = coin['type']
				through_coin['force'] = 5000
				pocket1_results.append(through_coin)
				break

		if 'red' not in through_coin.values() and strike_through_pocket[0]['type'] == 'red':
			coin_point = (strike_through_pocket[0]['x'], strike_through_pocket[0]['y'])
			intersection_point = hit_point(coin_point, pocket1_point, 1)
			intersection_point_x = intersection_point[0]
			intersection_point_y = intersection_point[1]
			intxy = intersection_point
			striker_positions = []
			red_hit = False
			for i in range(194,806,10):
				valid_position = True
				valid_strike = True
				red_strikes = {}
				striker_point = (striker_x, i)
				for j in positions:
					j_x = j['x']
					j_y = j['y']
					if (j_x > 792 and j_x < 902) and (j_y > i - 55 and j_y < i + 55):
						valid_position = False
					if valid_position and valid_strike:
						if j['type'] == 'red':
							continue
						if Point(j_x, j_y).intersects(LineString((striker_point, intersection_point, pocket1_point)).buffer(55)):
							valid_strike = False	
					if not valid_position or not valid_strike:
						break
				if valid_position and valid_strike:
					coin_pocket = (intersection_point, pocket1_point)
					coin_striker = (intersection_point,striker_point)
					angle_striker_coin_pocket = ang(coin_pocket, coin_striker)
					if angle_striker_coin_pocket > 140:
						# strike_line = Line(intersection_point, striker_point)
						# slope = strike_line.slope
						red_hit = True
						slope = (intersection_point_y - i) / (intersection_point_x - striker_x)
						angle = math.degrees(math.atan(slope))
						angle += 90
						red_strikes['angle'] = angle
						red_strikes['position'] = i
						red_strikes['angle_mutual'] = angle_striker_coin_pocket
						red_strikes['type'] = 'red'
						red_strikes['force'] = 5200
						pocket1_results.append(red_strikes)

			if not red_hit:
				print '...................connected shot1 ..................'
				red_coin_x = strike_through_pocket[0]['x']
				red_coin_y = strike_through_pocket[0]['y']
				red_coin = (red_coin_x, red_coin_y)
				intxn = hit_point(red_coin, pocket1_point, 1)
				intxn_x, intxn_y = intxn[0], intxn[1]
				for coin in positions:
					red_strikes = {}
					coin_x = coin['x']
					coin_y = coin['y']
					coin_point = (coin_x, coin_y)
					if coin_x > 846.7742 - 55 or coin['type'] == 'red':
						continue
					m = (coin_y - intxn_y) / (coin_x - intxn_x)
					int_y = m * (846.7742 - coin_x) + coin_y
					angle = math.degrees(math.atan(m))
					angle += 90
					int_x = 846.7742
					if int_y > 806.5416 or int_y < 193.5484:
						continue
					intersection_point = (int_x, int_y)
					coin_pocket = (intxn, pocket1_point)
					coin_striker = (intxn,coin_point)
					angle_striker_coin_pocket = ang(coin_pocket, coin_striker)
					path = True
					if angle_striker_coin_pocket < 150:
						continue
					for j in positions:
						if j == coin or j['type'] == 'red':
							continue
						pos_x = j['x']
						pos_y = j['y']
						if (pos_x > 792 and pos_x < 902) and (pos_y > int_y - 55 and pos_y < int_y + 55):
							path = False
							break
						if pos_x <= coin_x:
							continue
						if Point(pos_x, pos_y).intersects(LineString((coin_point,intersection_point)).buffer(55)):
							path = False
							break
					if path:
						red_hit = True
						red_strikes['angle'] = angle
						red_strikes['position'] = float(int_y)
						red_strikes['angle_mutual'] = angle_striker_coin_pocket
						red_strikes['type'] = 'red'
						red_strikes['force'] = 5500
						pocket1_results.append(red_strikes)
			if not red_hit:
				intersection_point = intxy
				intersection_point_x = intxy[0]
				intersection_point_y = intxy[1]
				red_strikes = {}
				striker_y = intxy[1]
				if intersection_point_y <= 550:
					mid_y = 1000
					mid_x = (intersection_point_x + striker_x) / 2
					mid_point = (mid_x, mid_y)
					striker_point = (striker_x, striker_y)
					striker = (striker_x, coin_point[1])
					path = True
					for j in positions:
						pos_x = j['x']
						pos_y = j['y']
						if (pos_x > 792 and pos_x < 902) and (pos_y > striker_y - 55 and striker_y < int_y + 55):
							path = False
							break
						if Point(pos_x, pos_y).intersects(LineString((striker, mid_point, intersection_point)).buffer(55)):
							path = False
							break
					if path:
						slope = (mid_y - striker_y) / (mid_x - striker_x)
						angle = math.degrees(math.atan(slope))
						angle += 90
						red_strikes['angle'] = angle
						red_strikes['position'] = strike_through_pocket[0]['y']
						red_strikes['angle_mutual'] = 180
						red_strikes['type'] = 'red'
						red_strikes['force'] = 8500
						pocket1_results.append(red_strikes)


	# striker_pos = [806, 194, 706, 606, 506, 406, 306]
	for i in range(806, 194, -50):
		striker_ok = True	
		striker_y = i
		striker_point = (striker_x, striker_y)

		for j in args:
			if j['type'] == 'stricker':
				continue
			x = j['x']
			y = j['y']
			if (x > 792 and x < 902) and (y > striker_y - 55 and y < striker_y + 55):
				striker_ok = False
				break
		if not striker_ok:
			continue

		strike_through_pocket_modified = []
		for coin in strike_through_pocket:
			coin_x = coin['x']
			coin_y = coin['y']
			if coin_y > 806 - 50 or coin_x > 846 - 50:
				continue
			coin_point = (coin_x, coin_y)
			intersection_point = hit_point(coin_point, pocket1_point, 1)
			intersection_point_x = intersection_point[0]
			intersection_point_y = intersection_point[1]
			point = {'x': intersection_point_x, 'y': intersection_point_y, 'type': coin['type'], 'id': coin['id']}
			strike_through_pocket_modified.append(point)

		strike_through_striker = clean_strikes(strike_through_pocket_modified, striker_point, positions, 55)

		striked = False
		if strike_through_striker:
			for coin in strike_through_striker:
				coin_x = coin['x']
				coin_y = coin['y']
				coin_pocket = ((coin_x, coin_y), pocket1_point)
				coin_striker = ((coin_x, coin_y),(striker_x, striker_y))
				angle_striker_coin_pocket = ang(coin_pocket, coin_striker)
				if angle_striker_coin_pocket < 145:
					continue
				coin_point = (coin_x, coin_y)
				slope = (coin_y - striker_y) / (coin_x - striker_x)
				angle = math.degrees(math.atan(slope))
				distance_striker_to_coin = math.hypot(coin_x - striker_x, coin_y - striker_y)
				distance_coin_to_pocket = math.hypot(pocket1_x - coin_x, pocket1_y - coin_y)
				total_distance = distance_striker_to_coin + distance_coin_to_pocket
				if angle_striker_coin_pocket >= 170:
				 	force = total_distance * 4.7
				elif angle_striker_coin_pocket < 170 and angle_striker_coin_pocket >= 150:
				 	force = total_distance * 5.1
				else:
				 	force = total_distance * 5.4
				if total_distance < 800:
				 	force =	total_distance * 5
				angle += 90
				strike = {'angle': angle, 'force': force, 'position': i, 'angle_mutual': angle_striker_coin_pocket, 'type': coin['type']}
				pocket1_results.append(strike)
			# 	striked = True
			# 	break
			# if striked:
			# 	break
	return_dict['pocket1'] = pocket1_results

def coin_positions4(args, return_dict):
	print 'Aiming for pocket4...' ,'\n'
	positions = []
	pocket4_results = []

	for coin in args:
		coin_x = coin['x']
		coin_y = coin['y']
		if coin_y < 194 + 55 and coin_x < 846 - 55:
			continue
		else:
			positions.append(coin)

	strike_through_pocket = clean_strikes(positions, pocket4_point, positions, 50)
	print 'clean14: ', strike_through_pocket, '\n'

	if strike_through_pocket:
		if 'red' in strike_through_pocket[0].values():
			coin_point = (strike_through_pocket[0]['x'], strike_through_pocket[0]['y'])
			intersection_point = hit_point(coin_point, pocket4_point, 4)
			intersection_point_x = intersection_point[0]
			intersection_point_y = intersection_point[1]
			striker_positions = []
			for i in range(194,806,10):
				valid_position = True
				valid_strike = True
				red_strikes = {}
				striker_point = (striker_x, i)
				for j in positions:
					j_x = j['x']
					j_y = j['y']
					if (j_x > 792 and j_x < 902) and (j_y > i - 55 and j_y < i + 55):
						valid_position = False
					if valid_position and valid_strike:
						if j['type'] == 'red':
							continue
						if Point(j_x, j_y).intersects(LineString((striker_point, intersection_point, pocket4_point)).buffer(55)):
							valid_strike = False	
					if not valid_position or not valid_strike:
						break
				if valid_position and valid_strike:
					coin_pocket = (intersection_point, pocket4_point)
					coin_striker = (intersection_point,striker_point)
					angle_striker_coin_pocket = ang(coin_pocket, coin_striker)
					if angle_striker_coin_pocket > 110:
						slope = (intersection_point_y - i) / (intersection_point_x - striker_x)
						angle = math.degrees(math.atan(slope))
						if intersection_point_x > striker_x:
							angle += 270
						else:
							angle += 90
						red_strikes['angle'] = angle
						red_strikes['position'] = i
						red_strikes['angle_mutual'] = angle_striker_coin_pocket
						red_strikes['type'] = 'red'
						red_strikes['force'] = 4000
						pocket4_results.append(red_strikes)

	striker_positions = []
	for i in range(194,806,50):
		valid_position = True
		for j in args:
			j_x = j['x']
			j_y = j['y']
			if (j_x > 792 and j_x < 902) and (j_y > i - 55 and j_y < i + 55):
				valid_position = False
				break
		if valid_position:
			striker_positions.append(i)

	# length = len(striker_positions)
	# striker_pos = [striker_positions[0], striker_positions[length / 2], striker_positions[length - 1]]
	for i in striker_positions:
		striker_y = i
		striker_point = (striker_x, striker_y)
		strike_through_pocket_modified = []
		for coin in strike_through_pocket:
			coin_x = coin['x']
			coin_y = coin['y']
			if coin_y < striker_y:
					continue
			coin_point = (coin_x, coin_y)
			intersection_point = hit_point(coin_point, pocket4_point, 4)
			intersection_point_x = intersection_point[0]
			intersection_point_y = intersection_point[1]
			point = {'x': intersection_point_x, 'y': intersection_point_y, 'type': coin['type'], 'id': coin['id']}
			strike_through_pocket_modified.append(point)

		strike_through_striker = clean_strikes(strike_through_pocket_modified, striker_point, positions, 55)

		striked = False
		if strike_through_striker:
			for coin in strike_through_striker:
				coin_x = coin['x']
				coin_y = coin['y']
				coin_pocket = ((coin_x, coin_y), pocket4_point)
				coin_striker = ((coin_x, coin_y),(striker_x, striker_y))
				angle_striker_coin_pocket = ang(coin_pocket, coin_striker)
				if angle_striker_coin_pocket < 110:
					continue
				coin_point = (coin_x, coin_y)
				slope = (coin_y - striker_y) / (coin_x - striker_x)
				angle = math.degrees(math.atan(slope))
				distance_striker_to_coin = math.hypot(coin_x - striker_x, coin_y - striker_y)
				distance_coin_to_pocket = math.hypot(pocket4_x - coin_x, pocket4_y - coin_y)
				total_distance = distance_striker_to_coin + distance_coin_to_pocket
				if total_distance < 500 and angle_striker_coin_pocket >= 170:
					force = 2000
				elif total_distance < 500 and angle_striker_coin_pocket < 170 and angle_striker_coin_pocket > 150:
					force = 3000
				elif angle_striker_coin_pocket < 170 and angle_striker_coin_pocket >= 150:
					force = 3800	
				else:
					force = 4200

				if coin_x > striker_x:
					angle += 270
				else:
					angle += 90
				strike = {'angle': angle, 'force': force, 'position': i, 'angle_mutual': angle_striker_coin_pocket, 'type': coin['type']}
				pocket4_results.append(strike)
			# 	striked = True
			# 	break
			# if striked:
			# 	break
	return_dict['pocket4'] = pocket4_results

def coin_positions2(args, return_dict):
	print 'Aiming for pocket2...' ,'\n'
	positions = []
	pocket2_results = []

	for coin in args:
		coin_x = coin['x']
		coin_y = coin['y']
		if coin_y > 806 - 50 and coin_x < 846 - 50:
			continue
		else:
			positions.append(coin)

	strike_through_pocket = clean_strikes(positions, pocket2_point, positions, 50)
	print 'clean12: ', strike_through_pocket, '\n'

	if strike_through_pocket:
		if 'red' in strike_through_pocket[0].values():
			coin_point = (strike_through_pocket[0]['x'], strike_through_pocket[0]['y'])
			intersection_point = hit_point(coin_point, pocket2_point, 2)
			intersection_point_x = intersection_point[0]
			intersection_point_y = intersection_point[1]
			striker_positions = []
			for i in range(806,194,-10):
				valid_position = True
				valid_strike = True
				red_strikes = {}
				striker_point = (striker_x, i)
				for j in positions:
					j_x = j['x']
					j_y = j['y']
					if (j_x > 792 and j_x < 902) and (j_y > i - 55 and j_y < i + 55):
						valid_position = False
					if valid_position and valid_strike:
						if j['type'] == 'red':
							continue
						if Point(j_x, j_y).intersects(LineString((striker_point, intersection_point, pocket2_point)).buffer(55)):
							valid_strike = False	
					if not valid_position or not valid_strike:
						break
				if valid_position and valid_strike:
					coin_pocket = (intersection_point, pocket2_point)
					coin_striker = (intersection_point,striker_point)
					angle_striker_coin_pocket = ang(coin_pocket, coin_striker)
					if angle_striker_coin_pocket > 110:
						slope = (intersection_point_y - i) / (intersection_point_x - striker_x)
						angle = math.degrees(math.atan(slope))
						if intersection_point_x > striker_x:
							angle += 270
						else:
							angle += 90
						red_strikes['angle'] = angle
						red_strikes['position'] = i
						red_strikes['angle_mutual'] = angle_striker_coin_pocket
						red_strikes['type'] = 'red'
						red_strikes['force'] = 4000
						pocket2_results.append(red_strikes)

	striker_positions = []
	for i in range(194,806,10):
		valid_position = True
		for j in args:
			j_x = j['x']
			j_y = j['y']
			if (j_x > 792 and j_x < 902) and (j_y > i - 55 and j_y < i + 55):
				valid_position = False
				break
		if valid_position:
			striker_positions.append(i)

	# length = len(striker_positions)
	# striker_pos = [striker_positions[length - 1], striker_positions[length / 2], striker_positions[0]]
	for i in striker_positions:
		striker_ok = True	
		striker_y = i
		striker_point = (striker_x, striker_y)
		strike_through_pocket_modified = []
		for coin in strike_through_pocket:
			coin_x = coin['x']
			coin_y = coin['y']
			if coin_y > striker_y:
					continue
			coin_point = (coin_x, coin_y)
			intersection_point = hit_point(coin_point, pocket2_point, 2)
			intersection_point_x = intersection_point[0]
			intersection_point_y = intersection_point[1]
			point = {'x': intersection_point_x, 'y': intersection_point_y, 'type': coin['type'], 'id': coin['id']}
			strike_through_pocket_modified.append(point)

		strike_through_striker = clean_strikes(strike_through_pocket_modified, striker_point, positions, 55)

		striked = False
		if strike_through_striker:
			for coin in strike_through_striker:
				coin_x = coin['x']
				coin_y = coin['y']
				coin_pocket = ((coin_x, coin_y), pocket2_point)
				coin_striker = ((coin_x, coin_y),(striker_x, striker_y))
				angle_striker_coin_pocket = ang(coin_pocket, coin_striker)
				if angle_striker_coin_pocket < 110:
					continue
				coin_point = (coin_x, coin_y)
				slope = (coin_y - striker_y) / (coin_x - striker_x)
				angle = math.degrees(math.atan(slope))
				distance_striker_to_coin = math.hypot(coin_x - striker_x, coin_y - striker_y)
				distance_coin_to_pocket = math.hypot(pocket2_x - coin_x, pocket2_y - coin_y)
				total_distance = distance_striker_to_coin + distance_coin_to_pocket
				if total_distance < 500 and angle_striker_coin_pocket >= 170:
					force = 2000
				elif total_distance < 500 and angle_striker_coin_pocket < 170 and angle_striker_coin_pocket > 150:
					force = 3000
				elif angle_striker_coin_pocket < 170 and angle_striker_coin_pocket >= 150:
					force = 3800	
				else:
					force = 4200

				if coin_x > striker_x:
					angle += 270
				else:
					angle += 90
				strike = {'angle': angle, 'force': force, 'position': i, 'angle_mutual': angle_striker_coin_pocket, 'type': coin['type']}
				pocket2_results.append(strike)
			# 	striked = True
			# 	break
			# if striked:
			# 	break
	return_dict['pocket2'] = pocket2_results	

socketIO.on('player_input', emit_response)
socketIO.emit('connect_game', {'playerKey': player2Key, 'gameKey': gameKey})
socketIO.on('connect_game', connection_response)
socketIO.on('your_turn', coin_positions)
socketIO.wait()