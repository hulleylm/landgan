import re
import numpy as np

text = open("GoogleEarth/dissertationKMLSanFran.txt", "r").read()

x = re.findall(r"(-122.[0-9]+),(3[0-9.]+)", text)
polygon = np.zeros((len(x),2))

isLat = True
for coord in range(len(x)):
    polygon[coord][0] = float(x[coord[0]])
    polygon[coord][1] = float(x[coord[1]])        

print("done")