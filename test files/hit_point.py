from sympy.geometry import *
import time
import math
start_time = time.time()
striker_x = 8153.2258
striker_y = 806
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
coin_x = 29
coin_y = 347.4147713818516
coin_point = (coin_x, coin_y)
circle = Circle(coin_point, 55)
line_coin_pocket = Line(coin_point, pocket1_point)
intersection_points = circle.intersection(line_coin_pocket)
intersection_point_x = float(intersection_points[0][0])
intersection_point_y = float(intersection_points[0][1])
intersection_point = (intersection_point_x, intersection_point_y)
line_coin_striker = Line(intersection_point, striker_point)
slope_coin_striker = line_coin_striker.slope
angle = math.degrees(math.atan(slope_coin_striker))
print intersection_point
print float(slope_coin_striker)
print angle + 90
print("---------- %s seconds -----------" % (time.time() - start_time))
