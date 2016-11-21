from pymongo import MongoClient
client = MongoClient('localhost', 27017)
db = client.carroms
game = db.games

xTransformFactor = 340
yTransformFactor = 30
localToGlobalRatio = 0.62

def point_conversion_to_local(x, y):
	x1 = (x - xTransformFactor) / localToGlobalRatio
	y1 = (y - yTransformFactor) / localToGlobalRatio
	return str(x1), str(y1)

def point_conversion_to_global(x, y):
	x1 = (x * localToGlobalRatio) + xTransformFactor
	y1 = (y * localToGlobalRatio) + yTransformFactor
	return x1, y1


print "(x, y) :"
x = float(raw_input())
y = float(raw_input())
x, y = point_conversion_to_global(x, y)
# x1 = float(raw_input())
# y1 = float(raw_input())
# x1, y1 = point_conversion_to_global(x1, y1)
# x2 = float(raw_input())
# y2 = float(raw_input())
# x2, y2 = point_conversion_to_global(x2, y2)
game.update_one({"gameKey":"1"},
 	{"$set" : {"currentPosition" : [
   
 		{ "x" : x, "y" : y, "type" : "black", "id" : "b1" }, 
 		# { "x" : x1, "y" : y1, "type" : "white", "id" : "w1" }, 
 		# { "x" : x2, "y" : y2, "type" : "black", "id" : "b1" }, 
 		{ "x" : 514.303156964414, "y" : 600, "type" : "stricker", "id" : "s1" } ,
 		# { "x" : 500, "y" : 500, "type" : "red", "id" : "r1" } 
 		] }},
 	upsert=False)



# db.games.update({"gameKey":"1"},
# 	{$set : {"currentPosition" :
# 	[{ "x" : 650, "y" : 340, "type" : "black", "id" : "b1" },
# 	 { "x" : 514.303156964414, "y" : 600, "type" : "stricker", "id" : "s1" }]}

