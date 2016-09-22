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
    	print ('Error function')

socketIO = SocketIO('10.7.90.8', 4000, Namespace)
print socketIO.connected

player1Key = 'T8uhv56xvs'
player2Key = 'GSwwserRd2'
gameKey = '9lVRq6Py7a3Vl1I0c4Fm'

def distance_between_points(point1, point2):
	x1, y1 = point1[0], point1[1]
	x2, y2 = point2[0], point2[1]
	distance = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
	return distance

def clean_strikes(coins, destination_point, positions, radius_total):
	strike_through = []
	for coin in coins:
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
	striker_x = 154
	striker_y = 194
	pocket4_x = 967.7419
	pocket4_y = 967.7419 
	pocket4_point = (pocket4_x, pocket4_y)
	striker_point = (154, 194)
	positions = args[0]['position']
	number_of_coins = len(positions)
	print '{}{}'.format('Number of coins = ', number_of_coins) 

	strike_through_pocket = clean_strikes(positions, pocket4_point, positions, 50)
	print 'clean1: ', strike_through_pocket, '\n'
	strike_through_striker = clean_strikes(strike_through_pocket, striker_point, positions, 55)
	print 'clean2: ', strike_through_striker, '\n'

	if strike_through_striker:
		for coin in strike_through_striker:
			coin_x = coin['x']
			coin_y = coin['y']
			coin_point = (coin_x, coin_y)
			print coin_point
			circle = Circle(coin_point, 55)
			line_coin_pocket = Line(coin_point, pocket4_point)
			intersection_points = circle.intersection(line_coin_pocket)
			intersection_point_x = round(float(intersection_points[0][0]))
			intersection_point_y = round(float(intersection_points[0][1]))

			point = (intersection_point_x, intersection_point_y)
			strike_line = Line(point, striker_point)
			slope = strike_line.slope
			angle = math.degrees(math.atan(slope))
			angle = round(angle, 2)
			break
	else:
		angle = 30

	angle += 90
	angle = int(angle)
	print '{} = {}'.format('Angle', angle)
	position = 194
	force = 3500
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