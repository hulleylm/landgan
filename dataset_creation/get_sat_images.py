import requests
import math
from PIL import Image
import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt
import json


def latLngToPoint(mapWidth, mapHeight, lat, lng):

    x = (lng + 180) * (mapWidth/360)
    y = ((1 - math.log(math.tan(lat * math.pi / 180) + 1 / math.cos(lat * math.pi / 180)) / math.pi) / 2) * mapHeight

    return [x, y]

def pointToLatLng(mapWidth, mapHeight, x, y):

    lng = x / mapWidth * 360 - 180

    n = math.pi - 2 * math.pi * y / mapHeight
    lat = (180 / math.pi * math. atan(0.5 * (math.exp(n) - math.exp(-n))))

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
    latStep = (abs(southWest[0] - northEast[0]))/22
    lngStep = (abs(southWest[1] - northEast[1]))/22

    return(latStep, lngStep)

def getLatStep(mapWidth, mapHeight, yScale, lat, lng):

    pointX, pointY = latLngToPoint(mapWidth, mapHeight, lat, lng)

    steppedPointY = pointY - ((mapHeight)/ yScale)
    newLat, originalLng = pointToLatLng(mapWidth, mapHeight, pointX, steppedPointY)

    latStep = lat - newLat

    return (latStep)

def requestImage(picHeight, picWidth, logoHeight, zoom, scale, maptype, lat, lng, row, col):

    center = str(lat) + "," + str(lng)
    url = "https://maps.googleapis.com/maps/api/staticmap?center=" + center + "&zoom=" + str(zoom) + "&size=" + str(picWidth) + "x" + str(picHeight+logoHeight) + "&key=" + api_key + "&maptype=" + maptype + "&scale=" + str(scale)
    filename = "dataset_creation/outputSatImg/" + AreaID + str(col) + "," + str(row) + ".png"

    img = "hi"

    # satImage = requests.get(url)
    # img = tf.image.decode_png(satImage.content, channels=3)
    # img = tf.image.crop_to_bounding_box(img, 0, 0, picWidth, picHeight) #Crop Google logo from base.
    # # image = tf.map_fn(lambda x: x/255.0, img)
    # # image = tf.image.per_image_standardization(img)
    # # arr_ = np.squeeze(img) # you can give axis attribute if you wanna squeeze in specific dimension
    # # plt.imshow(arr_)
    # # plt.show()

    # f = open(filename, 'wb')
    # f.write(satImage.content)
    # f.close()

    print("writtern to file: " + filename)

    return img

def requestElevations(mapWidth, mapHeight, image, bounds, elevSteps):

    elevations = np.zeros([picWidth, picHeight, 1])

    southWest = latLngToPoint(mapWidth, mapHeight, bounds[0], bounds[1])
    northWest = southWest
    northWest[1] = southWest[1] - elevSteps[1]

    point = northWest

    for i in range(21):
        url = "https://maps.googleapis.com/maps/api/elevation/json?locations="

        for j in range(21):
            latLng = pointToLatLng(mapWidth, mapHeight, point[0], point[1])
            url = url + str(latLng[0]) + "," + str(latLng[1]) + "|"
            point[0] = point[0] + elevSteps[0]
        elevRow = getElevation(url)
        #update "elevations" array with elevRow, steps of 5 pixels. (i think) 
        point[1] = point[1] + elevSteps[1]
    
    pass

def getElevation(url):

    url = url[:-1]
    url = url + "&key=" + api_key

    r = requests.get(url)
    r = r.text
    elevDict = json.loads(r)
    elevDict = elevDict["results"]
    
    elevRow = np.zeros(len(elevDict))
    for i in range(len(elevDict)):
        currentElev = elevDict[i]["elevation"]
        if currentElev == 0:
            currentElev = -0.001
        elevRow[i] = currentElev
    pass

# Bounding box for area to be scanned. AreaID is added to file name.
AreaID = "SF"
northWestLat = 37.806716
northWestLng = -122.477702
southEastLat = 37.7636132
southEastLng = -122.4319237

# Variables for API request (more info in README)
api_key = open("config.txt", "r", encoding="utf-16").read()
zoom = 15
logoHeight = 16 #(crop google logo off last 16 pixels)
picHeight = 150
picWidth = 150
scale = 1
maptype = "satellite"

# --- do not change variables below this point ---

mapHeight = 256
mapWidth = 256
xScale = math.pow(2, zoom) / (picWidth/mapWidth)
yScale = math.pow(2, zoom) / (picHeight/mapWidth)

startLat = northWestLat
startLng = northWestLng

startCorners = getImageBounds(mapWidth, mapHeight, xScale, yScale, startLat, startLng)

elevSteps = getElevStep(mapWidth, mapHeight, startCorners)

lngStep = startCorners[3] - startCorners[1]

col = 0
lat = startLat

while (lat >= southEastLat):
    lng = startLng
    row = 0

    while lng <= southEastLng:
        bounds = getImageBounds(mapWidth, mapHeight, xScale, yScale, lat, lng)
        image = requestImage(picHeight, picWidth, logoHeight, zoom, scale, maptype, lat, lng, row, col)
        requestElevations(mapWidth, mapHeight, image, bounds, elevSteps)
        row = row + 1
        lng = lng + lngStep

    col = col - 1
    lat = lat + getLatStep(mapWidth, mapHeight, yScale, lat, lng)