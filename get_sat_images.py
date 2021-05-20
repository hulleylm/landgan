import requests
import math
import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt
import json
from PIL import Image
from scipy.interpolate import griddata
from matplotlib.image import imread
import cv2
import pickle 
import csv

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

def checkIfLand(lat, lng):

    url = "https://maps.googleapis.com/maps/api/elevation/json?locations=" + str(lat) + "," + str(lng) + "&key=" + api_key
    r = requests.get(url)
    r = r.text
    elevDict = json.loads(r)
    elevation = elevDict["results"][0]["elevation"]

    if (elevation > 0):
        print("Land: " + str(lat) + "," + str(lng) + " point: " + str(row) + "," + str(col))
        return True
    else:
        print("X Sea: " + str(lat) + "," + str(lng) + " point: " + str(row) + "," + str(col))
        return False

def requestImage(picHeight, picWidth, logoHeight, zoom, scale, maptype, lat, lng, row, col):

    center = str(lat) + "," + str(lng)
    url = "https://maps.googleapis.com/maps/api/staticmap?center=" + center + "&zoom=" + str(zoom) + "&size=" + str(picWidth) + "x" + str(picHeight+(logoHeight*2)) + "&key=" + api_key + "&maptype=" + maptype + "&scale=" + str(scale)
    satImage = requests.get(url)
    img = tf.image.decode_png(satImage.content, channels=3)
    img = tf.image.crop_to_bounding_box(img, logoHeight, 0, picWidth, picHeight)

    # ---- Print the requested image ----
    RGBimage = tf.io.encode_png(img)
    filename = "testOutput/00image_" + str(row) + "," + str(col) + ".png"
    tf.io.write_file(filename, RGBimage)
    # -----

    return img

def requestElevations(mapWidth, mapHeight, bounds, elevSteps):

    elevationsPoints = numElevations+1
    elevations = np.zeros((elevationsPoints*elevationsPoints))

    southWest = latLngToPoint(mapWidth, mapHeight, bounds[0], bounds[1])

    origin = southWest.copy()
    origin[1] = southWest[1] - (elevSteps[0]*(numElevations - 1))
    point = origin.copy()

    for i in range(elevationsPoints):
        url = "https://maps.googleapis.com/maps/api/elevation/json?locations="
        point[0] = origin[0]

        for j in range(elevationsPoints):
            latLng = pointToLatLng(mapWidth, mapHeight, point[0], point[1])
            url = url + str(latLng[0]) + "," + str(latLng[1]) + "|"
            point[0] = point[0] + elevSteps[0]

        elevDict = getElevation(url)

        for k in range(len(elevDict)):
            currentElev = round(elevDict[k]["elevation"], 3)
            if currentElev < 0:
                currentElev = 0
            elevations[(i*elevationsPoints)+k] = currentElev            

        point[1] = point[1] + elevSteps[1]
    
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
    
    cubic = griddata(points, values, (grid_x, grid_y), method='cubic')

    cubic[cubic<minE] = minE
    cubic[cubic>maxE] = maxE

    cubic = cubic.reshape((cubic.shape[0], cubic.shape[1], 1))
    imputedArray = tf.convert_to_tensor(tf.constant(cubic))
    # imputedArray = tf.dtypes.cast(imputedArray, tf.uint8)

    return imputedArray

def getElevPoints():

    elevations = numElevations+1
    numPoints = (elevations)*(elevations)

    points = np.zeros((numPoints,2))
    count = 0

    for i in range(elevations):
        for j in range(elevations):
            points[count][0] = i*((picHeight-1)/numElevations)
            points[count][1] = j*((picHeight-1)/numElevations)
            count = count + 1

    return points

def createTensor(image, elevations):

    image = tf.dtypes.cast(image, tf.float64)
    # normalisedImage = normalise(image)
    normalisedElevs = normalise(elevations, minE, maxE)
    normalisedElevs = tf.map_fn(lambda x: x*255, normalisedElevs)
    combined = tf.concat([image, normalisedElevs], axis=2)

    # ---- Print heightmap ----
    # elevMax = tf.reduce_max(normalisedElevs)
    # elevMax = elevMax.numpy()
    # elevMin = tf.reduce_min(normalisedElevs)
    # elevMin = elevMin.numpy()
    # heightmap = tf.map_fn(lambda x: (((x - elevMin) * (255 - 0)) / (elevMax - elevMin)) + 0, normalisedElevs)
    # heightmap = tf.dtypes.cast(heightmap, tf.uint8)
    # heightmap = tf.io.encode_png(heightmap) #
    # tf.io.write_file("testOutput/height_" + str(row) + "," + str(col) + ".png", heightmap)
    #-----

    filename = "data/" + areaID + "tesssst_" + str(row) + "," + str(col) + ".obj"
    f = open(filename, 'wb')
    pickle.dump(combined, f)

    with open(r"pickledPoints.csv", 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(filename)

def normalise(arr, minE = 0, maxE = 255):

    normailsed = tf.map_fn(lambda x: (x - minE)/(maxE - minE), arr)

    return normailsed

# Bounding box for area to be scanned. AreaID is added to file name.
areaID = "testalps2"
northWestLat = 47.309535
northWestLng = 8.968262
southEastLat = 46.098575
southEastLng = 14.054704

# Variables for API request (more info in README)
api_key = open("config.txt", "r", encoding="utf-16").read()
zoom = 12
logoHeight = 22 #(crop google logo off last 16 pixels)
picHeight = 128
picWidth = 128
scale = 1
maptype = "satellite"

numElevations = 31 # Should be factor of pic height/ width -1
elevPoints = getElevPoints()
maxE = 8000
minE = -40

mapHeight = 256
mapWidth = 256
xScale = math.pow(2, zoom) / (picWidth/mapWidth)
yScale = math.pow(2, zoom) / (picHeight/mapWidth)

startLat = northWestLat
startLng = northWestLng

startCorners = getImageBounds(mapWidth, mapHeight, xScale, yScale, startLat, startLng)

lngStep = startCorners[3] - startCorners[1]

row = 0
lat = startLat

while (lat >= southEastLat):
    lng = startLng
    col = 0

    while lng <= southEastLng:
        if checkIfLand(lat, lng):
            bounds = getImageBounds(mapWidth, mapHeight, xScale, yScale, lat, lng)
            image = requestImage(picHeight, picWidth, logoHeight, zoom, scale, maptype, lat, lng, row, col)
            elevSteps = getElevStep(mapWidth, mapHeight, bounds)
            elevations = requestElevations(mapWidth, mapHeight, bounds, elevSteps)
            createTensor(image, elevations)
        col = col + 1
        lng = lng + lngStep

    row = row - 1
    lat = lat + getLatStep(mapWidth, mapHeight, yScale, lat, lng)