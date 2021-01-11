import requests
import csv
import pandas as pd
import matplotlib.path as mpltPath

def checkIfLand(path, lat, lng):
    if (path.contains_point([lng, lat])):
        center = str(lat) + "," + str(lng)
        requestImage(center)

def requestImage(center):
    url = "https://maps.googleapis.com/maps/api/staticmap?center=" + center + \
        "&zoom=16&size=640x640&key=" + api_key + "&maptype=satellite&scale=2"
    filename = AreaID + str(row) + "," + str(col) + ".png"
    r = requests.get(url)
    f = open(filename, 'wb')
    f.write(r.content)
    f.close()
    print("writtern to file")

api_key = open("config.txt", "r", encoding="utf-16").read()
polygon = pd.read_csv("satellite_images/sanFranPoly.csv").to_numpy()
path = mpltPath.Path(polygon)

# set overall area to be scanned
AreaID = "SanFran"
NWlat = 38.1273952
NWlng = -122.545723
SElat = 37.6223939
SElng = -122.3260534
step = 0.0120359

rows = int(round((NWlat - SElat)/step))
columns = int(round((abs(NWlng) - abs(SElng))/step))

lat = NWlat

for row in range(rows):
    lng = NWlng
    for col in range(columns):
        checkIfLand(path, lat, lng)
        lng = lng + step
        print (str(lat) + "," + str(lng) + " row: " + str(row) + " col: " + str(col))
    lat = lat - step

