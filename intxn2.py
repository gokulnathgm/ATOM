import time
from shapely.geometry import *
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
pocket4_point = (pocket2_x, pocket2_y)
coin_x = 400.1345
coin_y = 600.8463
m = (coin_y - pocket1_y) / (coin_x - pocket1_x)
coin_point = (coin_x, coin_y)
y = m * (846.7742 - coin_x) + coin_y
print y
print("---------- %s seconds -----------" % (time.time() - start_time))
