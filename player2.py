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
#socketIO = SocketIO('10.7.50.25', 4000)
print socketIO.connected

player1Key = 'T8uhv56xvs'
player2Key = 'GSwwserRd2'
gameKey = '9lVRq6Py7a3Vl1I0c4Fm'

# player1Key = 'p3'
# player2Key = 'p4'
# gameKey = '2'

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
				coin = {'x': coin['x1'], 'y': coin['y1']}
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
	print 'coin positions'
	print args
	angle = 0
	striker_x = 846
	striker_y = 806
	pocket1_x = 32.2581
	pocket1_y = 32.2581 
	pocket1_point = (pocket1_x, pocket1_y)
	striker_point = (striker_x, striker_y)
	positions = args[0]['position']
	number_of_coins = len(positions)
	print '{}{}'.format('Number of coins = ', number_of_coins) 

	strike_through_pocket = clean_strikes(positions, pocket1_point, positions, 50, False)
	print 'clean1: ', strike_through_pocket, '\n'

	strike_through_pocket_modified = []
	for coin in strike_through_pocket:
		coin_x = coin['x']
		coin_y = coin['y']
		if coin_y > 806 - 30 and coin_x < 846 - 30:
			continue
		coin_point = (coin_x, coin_y)
		circle = Circle(coin_point, 55)
		line_coin_pocket = Line(coin_point, pocket1_point)
		intersection_points = circle.intersection(line_coin_pocket)
		intersection_point_x = round(float(intersection_points[0][0]))
		intersection_point_y = round(float(intersection_points[0][1]))
		point = {'x': intersection_point_x, 'y': intersection_point_y, 'x1': coin_x, 'y1': coin_y}
		strike_through_pocket_modified.append(point)

	strike_through_striker = clean_strikes(strike_through_pocket_modified, striker_point, positions, 55, True)
	print 'clean2: ', strike_through_striker, '\n'

	if strike_through_striker:
		for coin in strike_through_striker:
			coin_x = coin['x']
			coin_y = coin['y']
			if coin_y < 194 + 30 and coin_x < 153 + 30:
				continue
			coin_point = (coin_x, coin_y)
			print coin_point
			circle = Circle(coin_point, 55)
			line_coin_pocket = Line(coin_point, pocket1_point)
			intersection_points = circle.intersection(line_coin_pocket)
			intersection_point_x = round(float(intersection_points[0][0]))
			intersection_point_y = round(float(intersection_points[0][1]))
			point = (intersection_point_x, intersection_point_y)
			strike_line = Line(point, striker_point)
			slope = strike_line.slope
			angle = math.degrees(math.atan(slope))
			angle = round(angle, 4)
			break
	else:
		angle = 45

	angle += 90
	#angle = int(angle)
	print '{} = {}'.format('Angle', angle)
	position = 806
	force = 3000
	print {'position': position, 'force': force, 'angle': angle}
	try:
		socketIO.emit('player_input', {'position': position, 'force': force, 'angle': angle})
	except Exception as e:
		print e

socketIO.on('player_input', emit_response)
socketIO.emit('connect_game', {'playerKey': player2Key, 'gameKey': gameKey})
socketIO.on('connect_game', connection_response)
socketIO.on('your_turn', coin_positions)
socketIO.wait()