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

def getCorners(picSize, lat, lng, zoom):

    mapSize = 256
    scale = math.pow(2, zoom) / (picSize/mapSize)
    centreX, centreY = latLngToPoint(mapSize, lat, lng)

    SWX = centreX -(mapSize/2)/ scale
    SWY = centreY + (mapSize/2)/ scale
    SWlat, SWlng = pointToLatLng(mapSize, SWX, SWY)

    NEX = centreX +(mapSize/2)/ scale
    NEY = centreY - (mapSize/2)/ scale
    NElat, NElng = pointToLatLng(mapSize, NEX, NEY)

    return(SWlat, SWlng, NElat, NElng)

def checkIfLand(path, lat, lng):

    if (path.contains_point([lng, lat])):
        center = str(lat) + "," + str(lng)
        requestImage(center)

def requestImage(center):

    picSize = 640
    url = "https://maps.googleapis.com/maps/api/staticmap?center=" + center + \
        "&zoom=16&size=" + picSize + "x" + picSize + "&key=" + api_key + "&maptype=satellite&scale=2"
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
AreaID = "SanFran"
NWlat = 38.1273952
NWlng = -122.545723
SElat = 37.6223939
SElng = -122.3260534
step = 0.0120359
zoom = 16

rows = int(round((NWlat - SElat)/step))
columns = int(round((abs(NWlng) - abs(SElng))/step))

lat = NWlat

for row in range(rows):
    lng = NWlng
    corners = getCorners(lat, lng, zoom)
    for col in range(columns):
        checkIfLand(path, lat, lng)
        print (str(lat) + "," + str(lng) + " row: " + str(row) + " col: " + str(col))
        print (str(corners))
        lng = lng + step
    lat = lat - step