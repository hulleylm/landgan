import numpy as np
from mpl_toolkits.mplot3d import Axes3D  
# Axes3D import has side effects, it enables using projection='3d' in add_subplot
import matplotlib.pyplot as plt
import random

#define parameters
terrainSize = 65 #should be 2^n + 1

def diamondSq(z):
    corners = random.randint(0,150)
    z[0][0] = z[terrainSize - 1][0]\
         = z[0][terrainSize -1] = z[terrainSize - 1][terrainSize - 1] = 20
    
    roughness = 20
    tileWidth = terrainSize -1

    while tileWidth > 1:
        halfSide = tileWidth // 2
    
        # set the diamond values (the centers of each tile)
        for x in range(0, terrainSize - 1, tileWidth):
            for y in range(0, terrainSize - 1, tileWidth):
                cornerSum = z[x][y] + \
                        z[x + tileWidth][y] + \
                        z[x][y + tileWidth] + \
                        z[x + tileWidth][y + tileWidth]

                avg = cornerSum / 4
                avg += random.randint(-roughness, roughness)

                z[x + halfSide][y + halfSide] = avg

        # set the square values (the midpoints of the sides)
        for x in range(0, terrainSize - 1, halfSide):
            for y in range((x + halfSide) % tileWidth, terrainSize - 1, tileWidth):
                avg = z[(x - halfSide + terrainSize - 1) % (terrainSize - 1)][y] + \
                  z[(x + halfSide) % (terrainSize - 1)][y] + \
                  z[x][(y + halfSide) % (terrainSize - 1)] + \
                  z[x][(y - halfSide + terrainSize - 1) % (terrainSize - 1)]

                avg /= 4.0
                avg += random.randint(-roughness, roughness)

                z[x][y] = avg

            # because the values wrap round, the left and right edges are equal, same with top and bottom
                if x == 0:
                    z[terrainSize - 1][y] = avg
                if y == 0:
                    z[x][terrainSize - 1] = avg

    # reduce the roughness in each pass, making sure it never gets to 0
        roughness = max(roughness // 2, 1)
        tileWidth //= 2

    return (z)#2D array of heights

#creates the mesh 'ground' which terrain rises from
x = np.linspace(0, terrainSize, terrainSize + 1)
y = np.linspace(0, terrainSize, terrainSize + 1)
z = np.zeros((terrainSize + 1, terrainSize + 1))
X, Y = np.meshgrid(x, y)
Z = diamondSq(z)

fig = plt.figure()
ax = plt.axes(projection="3d")
ax.plot_wireframe(X, Y, Z, color='green')
ax.set_xlabel('x')
ax.set_ylabel('y')
ax.set_zlabel('z')

ax = plt.axes(projection='3d')
ax.plot_surface(X, Y, Z, rstride=1, cstride=1, cmap='winter', edgecolor='none')
ax.set_title('Diamond Square Terrain')

plt.show()