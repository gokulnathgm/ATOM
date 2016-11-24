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
# striker_point = (striker_x, striker_y)
# def reflection_point(point1, point2):
# 	x1, y1 = point1[0], point1[1]
# 	x2, y2 = point2[0], point2[1]
# 	x = (((x1 * y2) + (x2 * y1)) / (y1 + y2))
# 	return (x, 0)
# print reflection_point((500, 600), (967.7419, 967.7419))

def reflection(point1, point2, pocket):
	x1, y1 = point1[0], point1[1]
	x2, y2 = point2[0], point2[1]
	if pocket == 4:
		y = 0
		x = ((x1 * y) + (x2 * y) - (x1 * y2) - (x2 * y1)) / ((2 * y) - y1 - y2)
		point = (x, y)
	elif pocket == 2:
		y = 1000
		x = ((x1 * y) + (x2 * y) - (x1 * y2) - (x2 * y1)) / ((2 * y) - y1 - y2)
		point = (x, y)
	elif pocket == 3 or pocket == 1:
		x = 1000
		y = ((x * y1) + (x * y2) - (x1 * y2) - (x2 * y1)) / ((2 * x) - x1 - x2)
		point = (x, y)
	return point	

print reflection((250, 250), pocket1_point, 1)
