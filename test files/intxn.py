import time
from sympy.geometry import *
start_time = time.time()
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
strike_line = Line((846.7742, 193.5484),(846.7742, 806.4516))
coin_x = 400.1345
coin_y = 600.8463
coin_point = (coin_x, coin_y)
coin_pocket = Line(coin_point, pocket1_point)
intersection_point = strike_line.intersection(coin_pocket)
print float(intersection_point[0][0]), float(intersection_point[0][1])
print("---------- %s seconds -----------" % (time.time() - start_time))
