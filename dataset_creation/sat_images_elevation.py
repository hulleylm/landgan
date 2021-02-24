import requests
import csv # to read polygon
import pandas as pd
import matplotlib.path as mpltPath
import math


def latLngToPoint(mapSize, lat, lng):

    x = (lng + 180) * (mapSize/360)
    y = ((1 - math.log(math.tan(lat * math.pi / 180) + 1 / math.cos(lat * math.pi / 180)) / math.pi) / 2) * mapSize

    return(x, y)

def pointToLatLng(mapSize, x, y):

    lng = x / mapSize * 360 - 180
    n = math.pi - 2 * math.pi * y / mapSize
    lat = (180 / math.pi * math. atan(0.5 * (math.exp(n) - math.exp(-n))))

    return(lat, lng)

def getImageBounds(picSize, mapSize, scale, lat, lng):

    centreX, centreY = latLngToPoint(mapSize, lat, lng)

    southWestX = centreX - (mapSize/2)/ scale
    southWestY = centreY + (mapSize/2)/ scale
    SWlat, SWlng = pointToLatLng(mapSize, southWestX, southWestY)

    northEastX = centreX + (mapSize/2)/ scale
    northEastY = centreY - (mapSize/2)/ scale
    NElat, NElng = pointToLatLng(mapSize, northEastX, northEastY)

    return[SWlat, SWlng, NElat, NElng]

def getLatStep(picSize, mapSize, scale, lat, lng):

    pointX, pointY = latLngToPoint(mapSize, lat, lng)

    steppedPointY = pointY - ((mapSize)/ scale)
    newLat, originalLng = pointToLatLng(mapSize, pointX, steppedPointY)

    latStep = lat - newLat

    return (latStep)

def checkIfLand(path, lat, lng):

    if (path.contains_point([lng, lat])):
        center = str(lat) + "," + str(lng)
        return True
    return False

def requestImage(picSize, zoom, center, row, col):

    url = "https://maps.googleapis.com/maps/api/staticmap?center=" + center + \
        "&zoom=16&size=" + str(picSize) + "x" + str(picSize) + "&key=" + api_key + "&maptype=satellite&scale=2"
    filename = AreaID + str(row) + "," + str(col) + ".png"
    r = requests.get(url)
    f = open(filename, 'wb')
    f.write(r.content)
    f.close()
    print("writtern to file" + filename)

api_key = open("config.txt", "r", encoding="utf-16").read()

# Bounding box for area to be scanned. AreaID is added to file name.
AreaID = "SanFran"
northWestLat = 38.1273952
northWestLng = -122.545723
southEastLat = 37.6223939
southEastLng = -122.3260534

zoom = 16
picSize = 640
mapSize = 256 #Google map size, keep at 256
scale = math.pow(2, zoom) / (picSize/mapSize)

startLat = northWestLat
startLng = northWestLng
startCorners = getImageBounds(picSize, mapSize, scale, startLat, startLng)
lngStep = startCorners[3] - startCorners[1]

col = 0
lat = startLat

while (lat >= southEastLat):
    lng = startLng
    row = 0

    while lng <= southEastLng:
        center = str(lat) + "," + str(lng)
        requestImage(picSize, zoom, center, row, col)
        row = row + 1
        lng = lng + lngStep

    col = col - 1
    lat = lat + getLatStep(picSize, mapSize, scale, lat, lng)