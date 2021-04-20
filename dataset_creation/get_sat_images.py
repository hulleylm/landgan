# Monday
# The elevations are wrong. Check that the long, lats being used in the request are correct.
# Must have data finished, normalised, example modelled on unity before end of day.
# If have time: look into model

import requests
import math
import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt
import json
from scipy.interpolate import griddata
from PIL import Image

def latLngToPoint(mapWidth, mapHeight, lat, lng):

    x = (lng + 180) * (mapWidth/360)
    y = ((1 - math.log(math.tan(lat * math.pi / 180) + 1 / math.cos(lat * math.pi / 180)) / math.pi) / 2) * mapHeight

    return [x, y]

def pointToLatLng(mapWidth, mapHeight, x, y):

    n = math.pi - 2 * math.pi * y / mapHeight
    lat = (180 / math.pi * math. atan(0.5 * (math.exp(n) - math.exp(-n))))

    lng = x / mapWidth * 360 - 180

    return(lat, lng)

def getImageBounds(mapWidth, mapHeight, xScale, yScale, lat, lng):

    centreX, centreY = latLngToPoint(mapWidth, mapHeight, lat, lng)

    southWestX = centreX - (mapWidth/2)/ xScale
    southWestY = centreY + (mapHeight/2)/ yScale
    SWlat, SWlng = pointToLatLng(mapWidth, mapHeight, southWestX, southWestY)

    northEastX = centreX + (mapWidth/2)/ xScale
    northEastY = centreY - (mapHeight/2)/ yScale
    NElat, NElng = pointToLatLng(mapWidth, mapHeight, northEastX, northEastY)

    return[SWlat, SWlng, NElat, NElng]

def getElevStep(mapWidth, mapHeight, bounds):
    southWest = latLngToPoint(mapWidth, mapHeight, bounds[0], bounds[1])
    northEast = latLngToPoint(mapWidth, mapHeight, bounds[2], bounds[3])

    latStep = (abs(southWest[1] - northEast[1]))/(numElevations - 1)
    lngStep = (abs(southWest[0] - northEast[0]))/(numElevations - 1)

    return(latStep, lngStep)

def getLatStep(mapWidth, mapHeight, yScale, lat, lng):

    pointX, pointY = latLngToPoint(mapWidth, mapHeight, lat, lng)

    steppedPointY = pointY - ((mapHeight)/ yScale)
    newLat, originalLng = pointToLatLng(mapWidth, mapHeight, pointX, steppedPointY)

    latStep = lat - newLat

    return (latStep)

def requestImage(picHeight, picWidth, logoHeight, zoom, scale, maptype, lat, lng, row, col):

    center = str(lat) + "," + str(lng)
    url = "https://maps.googleapis.com/maps/api/staticmap?center=" + center + "&zoom=" + str(zoom) + "&size=" + str(picWidth) + "x" + str(picHeight+logoHeight*2) + "&key=" + api_key + "&maptype=" + maptype + "&scale=" + str(scale)
    filename = "dataset_creation/outputSatImg/" + AreaID + str(col) + "," + str(row) + "aaaaaaaaaaaa.png"

    satImage = requests.get(url)
    # img = tf.image.decode_png(satImage.content, channels=3)
    # img = tf.image.crop_to_bounding_box(img, 0, 0, picWidth, picHeight) #Crop Google logo from base. need to crop top as well!
    # image = tf.map_fn(lambda x: x/255.0, img)
    # image = tf.image.per_image_standardization(img)
    # arr_ = np.squeeze(img) # you can give axis attribute if you wanna squeeze in specific dimension
    # plt.imshow(arr_)
    # plt.show()

    f = open(filename, 'wb')
    f.write(satImage.content)
    f.close()

    print("writtern to file: " + filename)

    pass

def requestElevations(mapWidth, mapHeight, image, bounds, elevSteps):

    elevations = np.zeros((numElevations*numElevations))
    TESTelevations = np.empty((numElevations, numElevations))

    southWest = latLngToPoint(mapWidth, mapHeight, bounds[0], bounds[1])

    origin = southWest.copy()
    origin[1] = southWest[1] - (elevSteps[0]*(numElevations - 1))
    point = origin.copy()

    for i in range(numElevations):
        url = "https://maps.googleapis.com/maps/api/elevation/json?locations="
        point[0] = origin[0]

        for j in range(numElevations):
            latLng = pointToLatLng(mapWidth, mapHeight, point[0], point[1])
            url = url + str(latLng[0]) + "," + str(latLng[1]) + "|"
            point[0] = point[0] + elevSteps[0]

        elevDict = getElevation(url)

        for k in range(len(elevDict)):
            currentElev = round(elevDict[k]["elevation"], 3)
            if currentElev < 0:
                currentElev = 0
            # currentElev = currentElev/90
            elevations[(i*numElevations)+k] = currentElev
            TESTelevations[i][k] = currentElev #next try reshape instead
            

        point[1] = point[1] + elevSteps[1]
    
    np.savetxt("test.csv", TESTelevations, delimiter=",")
    elevationsMatrix = imputateElevs(elevations)
    return elevationsMatrix

def getElevation(url):

    url = url[:-1]
    url = url + "&key=" + api_key

    r = requests.get(url)
    r = r.text
    elevDict = json.loads(r)
    elevDict = elevDict["results"]
    
    return elevDict

def imputateElevs(elevations):

    grid_x, grid_y = np.mgrid[0:picWidth:1, 0:picHeight:1]

    points = elevPoints
    values = elevations

    grid_z0 = griddata(points, values, (grid_x, grid_y), method='nearest')
    grid_z1 = griddata(points, values, (grid_x, grid_y), method='linear')
    grid_z2 = griddata(points, values, (grid_x, grid_y), method='cubic')
    grid_z2[grid_z2<0] = 0

    
    saveImage(grid_z0, "zero")
    saveImage(grid_z1, "one")
    saveImage(grid_z2, "two")

    np.savetxt("z.csv", grid_z0, delimiter=",")
    np.savetxt("o.csv", grid_z1, delimiter=",")
    np.savetxt("t.csv", grid_z2, delimiter=",")

    pass

def getElevPoints():

    numPoints = numElevations*numElevations
    points = np.zeros((numPoints,2))
    count = 0

    for i in range(numElevations):
        for j in range(numElevations):
            points[count][0] = i*((picHeight-1)/numElevations)
            points[count][1] = j*((picHeight-1)/numElevations)
            count = count + 1

    return points

def saveImage(arr, name):

    im = Image.fromarray(arr.astype(np.uint8))
    im.save(name + ".png")

# Bounding box for area to be scanned. AreaID is added to file name.
AreaID = "SF"
northWestLat = 37.806716
northWestLng = -122.477702
southEastLat = 37.7636132
southEastLng = -122.4319237

# Variables for API request (more info in README)
api_key = open("config.txt", "r", encoding="utf-16").read()
zoom = 15
logoHeight = 22 #(crop google logo off last 16 pixels)
picHeight = 257
picWidth = 257
scale = 1
maptype = "satellite"

numElevations = 64 # Should be factor of pic height/ width -1
elevPoints = getElevPoints()

# --- do not change variables below this point ---

mapHeight = 256
mapWidth = 256
xScale = math.pow(2, zoom) / (picWidth/mapWidth)
yScale = math.pow(2, zoom) / (picHeight/mapWidth)

startLat = northWestLat
startLng = northWestLng

startCorners = getImageBounds(mapWidth, mapHeight, xScale, yScale, startLat, startLng)

lngStep = startCorners[3] - startCorners[1]

col = 0
lat = startLat

while (lat >= southEastLat):
    lng = startLng
    row = 0

    while lng <= southEastLng:
        bounds = getImageBounds(mapWidth, mapHeight, xScale, yScale, lat, lng)
        image = requestImage(picHeight, picWidth, logoHeight, zoom, scale, maptype, lat, lng, row, col)
        elevSteps = getElevStep(mapWidth, mapHeight, bounds)
        elevations = requestElevations(mapWidth, mapHeight, image, bounds, elevSteps)
        row = row + 1
        lng = lng + lngStep

    col = col - 1
    lat = lat + getLatStep(mapWidth, mapHeight, yScale, lat, lng)