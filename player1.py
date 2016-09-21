from socketIO_client import SocketIO
from sympy.geometry import *
from sympy import sympify
import random
import math

socketIO = SocketIO('10.7.90.8', 4000)
print socketIO.connected

player1Key = 'T8uhv56xvs'
player2Key = 'GSwwserRd2'
gameKey = '9lVRq6Py7a3Vl1I0c4Fm'

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
	print 'coin positions'
	print args

	angle = 0
	striker_x = 153.2258
	striker_y = 193.5484
	pocket4_x = 967.7419
	pocket4_y = 967.7419 
	pocket4_point = (pocket4_x, pocket4_y)
	striker_point = (154, 194)
	strike_through = []
	positions = args[0]['position']
	number_of_coins = len(positions)
	print '{}{}'.format('Number of coins = ', number_of_coins) 
	for coin in positions:
		coin_x = coin['x']
		coin_y = coin['y']
		coin_point = (coin_x, coin_y)
		line_coin_pocket = Line(coin_point, pocket4_point)
		distance_coin_pocket = distance_between_points(coin_point, pocket4_point)
		path = True
		for coin_subset in positions:
			coin_subset_x = coin_subset['x']
			coin_subset_y = coin_subset['y']
			coin_subset_point = (coin_subset_x, coin_subset_y)
			distance_subset_coin_pocket = distance_between_points(coin_subset_point, pocket4_point)
			distance_between_coins = distance_between_points(coin_point, coin_subset_point)
			if(distance_coin_pocket > distance_between_coins and distance_coin_pocket > distance_subset_coin_pocket):
				if float(line_coin_pocket.perpendicular_segment(coin_subset_point).length) < 50:
					path = False
					break
		if path:
			strike_through.append(coin_point)

	for coin in strike_through:
		print coin
		circle = Circle(coin, 55)
		line_coin_pocket = Line(coin, pocket4_point)
		intersection_points = circle.intersection(line_coin_pocket)
		intersection_point_x = round(float(intersection_points[0][0]))
		intersection_point_y = round(float(intersection_points[0][1]))

		point = (intersection_point_x, intersection_point_y)
		strike_line = Line(point, striker_point)
		slope = strike_line.slope
		angle = math.degrees(math.atan(slope))
		angle = round(angle, 2)
		break

	angle += 90
	angle = int(angle)
	print '{} = {}'.format('Angle', angle)
	position = 200
	force = 2500
	print {'position': position, 'force': force, 'angle': angle}
	socketIO.emit('player_input', {'position': position, 'force': force, 'angle': angle})
	socketIO.on('player_input', emit_response)

socketIO.emit('connect_game', {'playerKey': player1Key, 'gameKey': gameKey})
socketIO.on('connect_game', connection_response)
socketIO.on('your_turn', coin_positions)
socketIO.wait()

