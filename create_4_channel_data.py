import pickle
import tensorflow as tf
import numpy as np
import os

files = os.listdir('data/')
allData = np.zeros((len(files),128,128,4))

for i, fileName in enumerate(files):
    filehandler = open("data/" + fileName, 'rb')
    tens = pickle.load(filehandler)
    img = tf.dtypes.cast(tens, tf.uint8)
    RGBAimage = tf.io.encode_png(img)
    filename = "dataRGBA/" + str(i) + ".png"
    tf.io.write_file(filename, RGBAimage)
    print(filename)