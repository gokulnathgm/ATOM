import time
import math
start_time = time.time()
def distance_between_points(point1, point2):
	x1, y1 = point1[0], point1[1]
	x2, y2 = point2[0], point2[1]
	distance = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
	return distance
pocket4_x = 967.7419
pocket4_y = 967.7419
pocket3_x = 32.2581
pocket3_y = 967.7419
point1 = (pocket4_x, pocket4_y)
point2 = (pocket3_x, pocket3_y)
distance = distance_between_points(point1, point2)
print distance
print("---------- %s seconds -----------" % (time.time() - start_time))

