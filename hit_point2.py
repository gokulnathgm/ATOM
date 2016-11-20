import time
import math
start_time = time.time()
striker_x = 153.2258
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
m = (pocket1_y - coin_y) / (pocket1_x - coin_x)
int_x = coin_x - (55 / math.sqrt(1 + m * m))
int_y = coin_y +  (m * (int_x - coin_x))
intx = (int_x, int_y)
m = (int_y - striker_y) / (int_x - striker_x)
angle = math.degrees(math.atan(m))
print intx
print m
print angle + 90
print("---------- %s seconds -----------" % (time.time() - start_time))


