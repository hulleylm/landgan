import pickle
import tensorflow as tf
import numpy as np
import os

files = os.listdir('data/')
allData = np.zeros((len(files),128,128,4))

for i, fileName in enumerate(files):
    filehandler = open("data/" + fileName, 'rb')
    tens = pickle.load(filehandler)
    image, elev = tf.split(tens, [3, 1], 2)

    image = tf.dtypes.cast(image, tf.uint8)

    originalElev = tf.map_fn(lambda x: (8040*x - 40)/255, elev)
    elevMax = tf.reduce_max(originalElev)
    elevMax = elevMax.numpy()
    elevMin = tf.reduce_min(originalElev)
    elevMin = elevMin.numpy()
    heightmap = tf.map_fn(lambda x: (((x - elevMin) * (255 - 0)) / (elevMax - elevMin)) + 0, originalElev)
    heightmap = tf.dtypes.cast(heightmap, tf.uint8)
    # heightmapImg = tf.io.encode_png(heightmap) #
    # tf.io.write_file("testOutputH/height_" + str(i) + ".png", heightmapImg)
    

    combined = tf.concat([image, heightmap], axis=2)
    # test = combined.numpy()
    RGBAimage = tf.io.encode_png(combined)
    filename = "dataRGBA/" + str(i) + ".png"
    tf.io.write_file(filename, RGBAimage)
    print(filename)