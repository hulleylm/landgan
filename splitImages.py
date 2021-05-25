import tensorflow as tf
import numpy as np
from PIL import Image
import os

files = os.listdir('dissertation/final/images/data/512RGBAFin/splitMe/')

epochs = 0

for i, fileName in enumerate(files):
    image = Image.open("dissertation/final/images/data/512RGBAFin/splitMe/" + fileName)

    tf_image = np.array(image)
    tens = tf.convert_to_tensor(tf_image)
    img, elev = tf.split(tens, [3, 1], 2)

    comb = tf.io.encode_png(tens)
    tf.io.write_file("dissertation/final/images/data/512RGBAFin/combo/" + str(i) + ".png", comb)
    
    img = tf.io.encode_png(img)
    tf.io.write_file("dissertation/final/images/data/512RGBAFin/images/" + str(i) + ".png", img)
    
    elev = tf.io.encode_png(elev)
    tf.io.write_file("dissertation/final/images/data/512RGBAFin/height/" + str(i) + ".png", elev)