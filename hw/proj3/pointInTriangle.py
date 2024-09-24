from matplotlib.path import Path
import numpy as np

# triPoints is a list of 3x2 arrays like this:
# [[25.774252, -80.190262], 
#  [18.466465, -66.118292], 
#  [32.321384, -64.757375]]
#
# points is an nx2 array like this:
# [[27.254629577800088, -74.928515625],
#   ...
#  [32.321384688234444, -64.757375978]]

def assignPts2Triangles(triangles, points):
	triLabels = np.nan * ones(len(points))
	for i, pt in enumerate(points):
		for j, tri in enumerate(triangles):
			if tri.contains_point(point):
				triLabels[i] = j

triPaths = []
for tpts in triPoints:
	triPaths.append(Path(tpts))

triLabels = assignPts2Triangles(triPaths, points)
