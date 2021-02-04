import requests
import csv
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

    SWX = centreX - (mapSize/2)/ scale
    SWY = centreY + (mapSize/2)/ scale
    SWlat, SWlng = pointToLatLng(mapSize, SWX, SWY)

    NEX = centreX + (mapSize/2)/ scale
    NEY = centreY - (mapSize/2)/ scale
    NElat, NElng = pointToLatLng(mapSize, NEX, NEY)

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

def requestImage(picSize, zoom, center):

    url = "https://maps.googleapis.com/maps/api/staticmap?center=" + center + \
        "&zoom=16&size=" + str(picSize) + "x" + str(picSize) + "&key=" + api_key + "&maptype=satellite&scale=2"
    filename = AreaID + str(row) + "," + str(col) + ".png"
    r = requests.get(url)
    f = open(filename, 'wb')
    f.write(r.content)
    f.close()
    print("writtern to file")

api_key = open("config.txt", "r", encoding="utf-16").read()
polygon = pd.read_csv("satellite_images/sanFranPoly.csv").to_numpy()
path = mpltPath.Path(polygon)

# ToDo set NE and SE as largest/ smallest vales in polygon
# NWlat, NWlng, SWllat, SWlng = getScanBounds(path)
AreaID = "SanFran"
NWlat = 38.1273952
NWlng = -122.545723
SElat = 37.6223939
SElng = -122.3260534
step = 0.0120359
zoom = 16
picSize = 640
mapSize = 256
scale = math.pow(2, zoom) / (picSize/mapSize)

rows = int(round((NWlat - SElat)/step))
columns = int(round((abs(NWlng) - abs(SElng))/step))

startLat = NWlat
startLng = NWlng
startCorners = getImageBounds(picSize, mapSize, scale, startLat, startLng)
lngStep = startCorners[3] - startCorners[1]

lat = startLat
for row in range(rows):
    lng = startLng
    for col in range(columns):
        if (path.contains_point([lng, lat])):
            corners = getImageBounds(picSize, mapSize, scale, lat, lng)
            center = str(lat) + "," + str(lng)
            print(str(center) + " corners: " + str(corners))
            requestImage(picSize, zoom, center)
        lng = lng + lngStep
    latStep = getLatStep(picSize, mapSize, scale, lat, lng)
    lat = lat + latStep