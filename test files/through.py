from sympy.geometry import *
from shapely.geometry import *
import time
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
		intersection_point = (int_x, int_y)
		path = True
		for j in positions:
			pos_x = j['x']
			pos_y = j['y']
			if Point(pos_x, pos_y).intersects(LineString((coin_point,intersection_point)).buffer(55)):
				path = False
				break
		if path:
			through_coins.append(coin);
	return through_coins

start_time = time.time()
positions = [{u'y': 637.1721717446608, u'x': 34.64849887596901, u'type': u'black', u'id': u'b1'}, {u'y': 604.4487114400504, u'x': 628.2428484614, u'type': u'black', u'id': u'b2'}, {u'y': 338.9532291148154, u'x': 335.76191218013435, u'type': u'black', u'id': u'b3'}, {u'y': 375.1212674615185, u'x': 688.6863993769005, u'type': u'black', u'id': u'b4'}, {u'y': 298.064583571095, u'x': 619.3538396589995, u'type': u'black', u'id': u'b5'}, {u'y': 433.261616937456, u'x': 75.89643085636467, u'type': u'black', u'id': u'b6'}, {u'y': 831.5579499590237, u'x': 158.78205992763642, u'type': u'black', u'id': u'b7'}, {u'y': 930.2437717391282, u'x': 581.1066115970549, u'type': u'black', u'id': u'b8'}, {u'y': 544.7769024801631, u'x': 728.5591273889611, u'type': u'black', u'id': u'b9'}, {u'y': 470.2417671799986, u'x': 543.774573029412, u'type': u'white', u'id': u'w1'}, {u'y': 428.8966050138874, u'x': 599.7762029439905, u'type': u'white', u'id': u'w2'}, {u'y': 481.8976113558992, u'x': 264.87592636745535, u'type': u'white', u'id': u'w3'}, {u'y': 679.1306964648693, u'x': 262.85806160019416, u'type': u'white', u'id': u'w4'}, {u'y': 588.551674098249, u'x': 363.36651830687157, u'type': u'white', u'id': u'w5'}, {u'y': 730.6054988146498, u'x': 621.0189203763877, u'type': u'white', u'id': u'w6'}, {u'y': 778.1896907508481, u'x': 463.46806332139676, u'type': u'white', u'id': u'w7'}, {u'y': 285.7123255445092, u'x': 494.5101642850617, u'type': u'white', u'id': u'w8'}, {u'y': 340.88865761734723, u'x': 401.74766419217957, u'type': u'white', u'id': u'w9'}, {u'y': 328.1237091399258, u'x': 926.6888063514755, u'type': u'red', u'id': u'r1'}, {u'y': 101.30039823496105, u'x': 73.36058272563768, u'type': u'stricker', u'id': u's1'}]
coins = [{u'y': 930.2437717391282, u'x': 581.1066115970549, u'type': u'black', u'id': u'b8'}, {u'y': 544.7769024801631, u'x': 728.5591273889611, u'type': u'black', u'id': u'b9'}, {u'y': 470.2417671799986, u'x': 543.774573029412, u'type': u'white', u'id': u'w1'}, {u'y': 428.8966050138874, u'x': 599.7762029439905, u'type': u'white', u'id': u'w2'}, {u'y': 481.8976113558992, u'x': 264.87592636745535, u'type': u'white', u'id': u'w3'}]
pocket = (1000, 1000)
result = through_coins(coins, positions)
print("---------- %s seconds -----------" % (time.time() - start_time))