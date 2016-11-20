import time
import math
start_time = time.time()
pocket4_x = 967.7419
pocket4_y = 967.7419
pocket3_x = 32.2581
pocket3_y = 967.7419
distance = math.hypot(pocket4_x - pocket3_x, pocket4_y - pocket3_y)
print distance
print("---------- %s seconds -----------" % (time.time() - start_time))
