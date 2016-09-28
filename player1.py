from socketIO_client import SocketIO
from sympy.geometry import *
from sympy import sympify
import random
import math
from socketIO_client import BaseNamespace

class Namespace(BaseNamespace):
    def on_connect(self):
        print('[Connected]')

    def on_disconnect(self):
    	print ('[Disconnected]')

socketIO = SocketIO('10.7.90.8', 4000, Namespace)
print socketIO.connected

player1Key = 'T8uhv56xvs'
player2Key = 'GSwwserRd2'
gameKey = '9lVRq6Py7a3Vl1I0c4Fm'

# player1Key = 'p21'
# player2Key = 'GSwwserRd2'
# gameKey = '2'

first_strike = True
set_strike_first = False

def distance_between_points(point1, point2):
	x1, y1 = point1[0], point1[1]
	x2, y2 = point2[0], point2[1]
	distance = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
	return distance

def clean_strikes(coins, destination_point, positions, radius_total, check):
	strike_through = []
	for coin in coins:
		if check == False and coin['type'] == 'stricker':
			continue

		coin_x = coin['x']
		coin_y = coin['y']
		coin_point = (coin_x, coin_y)
		line_coin_pocket = Line(coin_point, destination_point)
		distance_coin_pocket = distance_between_points(coin_point, destination_point)
		path = True
		for coin_subset in positions:
			if coin_subset['type'] == 'stricker':
				continue
			coin_subset_x = coin_subset['x']
			coin_subset_y = coin_subset['y']
			coin_subset_point = (coin_subset_x, coin_subset_y)
			distance_subset_coin_pocket = distance_between_points(coin_subset_point, destination_point)
			distance_between_coins = distance_between_points(coin_point, coin_subset_point)
			if(distance_coin_pocket > distance_between_coins and distance_coin_pocket > distance_subset_coin_pocket):
				if float(line_coin_pocket.perpendicular_segment(coin_subset_point).length) < radius_total:
					path = False
					break
		if path:
			if check:
				coin = {'x': coin['x1'], 'y': coin['y1'], 'type': coin['type']}
				strike_through.append(coin)
			else:
				strike_through.append(coin)

	return strike_through

def emit_response(*args):
	print 'Emit response'
	print args, '\n'

def connection_response(*args):
	print 'connection_response'
	print args

def coin_positions(*args):
	global first_strike
	global set_strike_first

	if first_strike:
		set_strike_first = True
		first_strike = False
	else:
		set_strike_first = False
		print 'coin positions'
		print args
		angle = 0

		striker_x = 153.2258
		striker_y = 194
		# pocket4_x = 967.7419
		# pocket4_y = 967.7419 
		# pocket3_x = 32.2581
		# pocket3_y = 967.7419
		# pocket2_x = 967.7419
		# pocket2_y = 32.2581
		# pocket1_x = 32.2581
		# pocket1_y = 32.2581

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
		number_of_coins = len(positions)
		print '{}{}'.format('Number of coins = ', number_of_coins) 

		no_strike = False
		pocket2 = True
		for i in xrange(194, 806, 100):
			striker_ok = True	
			striker_y = i
			striker_point = (striker_x, striker_y)

			for j in positions:
				if j['type'] == 'stricker':
					continue
				x = j['x']
				y = j['y']
				if (x > 99 and x < 209) and (y > striker_y - 55 and y < striker_y + 55):
					striker_ok = False
					break
			if not striker_ok:
				if i == 794:
					no_strike = True
				continue

			strike_through_pocket = clean_strikes(positions, pocket4_point, positions, 50, False)
			print 'clean1: ', strike_through_pocket, '\n'

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
				point = {'x': intersection_point_x, 'y': intersection_point_y, 'x1': coin_x, 'y1': coin_y, 'type': coin['type']}
				strike_through_pocket_modified.append(point)

			strike_through_striker = clean_strikes(strike_through_pocket_modified, striker_point, positions, 55, True)
			print 'clean2: ', strike_through_striker, '\n'

			if strike_through_striker:
				coin = strike_through_striker[len(strike_through_striker)-1]
				coin_x = coin['x']
				coin_y = coin['y']
				print coin
				if coin_y < 194 + 50 or coin_x < 153 + 50:
					continue
				coin_point = (coin_x, coin_y)
				print coin_point
				circle = Circle(coin_point, 55)
				line_coin_pocket = Line(coin_point, pocket4_point)
				intersection_points = circle.intersection(line_coin_pocket)
				intersection_point_x = float(intersection_points[0][0])
				intersection_point_y = float(intersection_points[0][1])
				point = (intersection_point_x, intersection_point_y)
				strike_line = Line(point, striker_point)
				slope = strike_line.slope
				angle = math.degrees(math.atan(slope))
				pocket2 = False
				break
			else:
				angle = -55

		if pocket2:
			print 'Aiming for pocket2'
			no_strike = False
			for i in xrange(806, 194, -100):
				striker_ok = True	
				striker_y = i
				striker_point = (striker_x, striker_y)

				for j in positions:
					if j['type'] == 'stricker':
						continue
					x = j['x']
					y = j['y']
					if (x > 99 and x < 209) and (y > striker_y - 55 and y < striker_y + 55):
						striker_ok = False
						break
				if not striker_ok:
					if i == 206:
						no_strike = True
					continue

				strike_through_pocket = clean_strikes(positions, pocket2_point, positions, 50, False)
				print 'clean1: ', strike_through_pocket, '\n'

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
					point = {'x': intersection_point_x, 'y': intersection_point_y, 'x1': coin_x, 'y1': coin_y, 'type': coin['type']}
					strike_through_pocket_modified.append(point)

				strike_through_striker = clean_strikes(strike_through_pocket_modified, striker_point, positions, 55, True)
				print 'clean2: ', strike_through_striker, '\n'

				if strike_through_striker:
					coin = strike_through_striker[len(strike_through_striker)-1]
					coin_x = coin['x']
					coin_y = coin['y']
					print coin
					if coin_y > 806 - 50 or coin_x < 153 + 50:
						continue
					coin_point = (coin_x, coin_y)
					print coin_point
					circle = Circle(coin_point, 55)
					line_coin_pocket = Line(coin_point, pocket2_point)
					intersection_points = circle.intersection(line_coin_pocket)
					intersection_point_x = float(intersection_points[0][0])
					intersection_point_y = float(intersection_points[0][1])
					point = (intersection_point_x, intersection_point_y)
					strike_line = Line(point, striker_point)
					slope = strike_line.slope
					angle = math.degrees(math.atan(slope))
					break
				else:
					angle = -65

	if set_strike_first:
		force = 4000
		position = 400
		angle = 110

	else:			
		angle += 90
		print '{} = {}'.format('Angle', angle)
		position = i
		if no_strike:
			position = random.randint(194, 794)
			angle = random.randint(30, 150)
		force = 2500
		if set_strike_first:
			force = 4000
			position = 500
			angle = 90

	print {'position': position, 'force': force, 'angle': angle}
	try:
		socketIO.emit('player_input', {'position': position, 'force': force, 'angle': angle})
	except Exception as e:
		print e

socketIO.on('player_input', emit_response)
socketIO.emit('connect_game', {'playerKey': player1Key, 'gameKey': gameKey})
socketIO.on('connect_game', connection_response)
socketIO.on('your_turn', coin_positions)
socketIO.wait()