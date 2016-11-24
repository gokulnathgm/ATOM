def reflection_point(point1, point2):
	x1, y1 = point1[0], point1[1]
	x2, y2 = point2[0], point2[1]
	x = (((x1 * y2) + (x2 * y1)) / (y1 + y2))
	return (x, 0)
print reflection_point((500, 600), (967.7419, 0))