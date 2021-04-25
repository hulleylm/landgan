import pickle
import tensorflow as tf
import numpy as np

maxE = 8000
minE = -40

filehandler = open("data/SanFran_0,3.obj", 'rb') 
tens = pickle.load(filehandler)

image, elev = tf.split(tens, [3, 1], 2)

image = tf.map_fn(lambda x: x*255, image)
image = tf.dtypes.cast(image, tf.uint8)
RGBAimage = tf.io.encode_png(image)
tf.io.write_file("image.png", RGBAimage)

elev = tf.map_fn(lambda x: x*(maxE-minE)+minE, elev)
elevNp = elev.numpy()

elevMax = tf.reduce_max(elev)
elevMax = elevMax.numpy()
elevMin = tf.reduce_min(elev)
elevMin = elevMin.numpy()
test1 = (3.2*(elevMax-elevMin))+elevMin
test2 = (0*(elevMax-elevMin))+elevMin
elev = tf.map_fn(lambda x: (x*(elevMax-elevMin))+elevMin, elev)
# RGBAimage = tf.io.encode_png(elev)
# tf.io.write_file("elev.png", RGBAimage)

elevMaxNp = np.amax(elevNp)

elevMinNp = np.amin(elevNp)

test1Np = (3.2*(elevMaxNp-elevMinNp))+elevMinNp
test2Np = (0*(elevMaxNp-elevMinNp))+elevMinNp
elevNp = np.reshape(elevNp, (257,257))
np.savetxt("nearest.csv", elevNp, delimiter=",")
for i in elevNp:
    for j in elevNp[i]:
        pass
print("hi")
# elevNp = tf.map_fn(lambda x: (x*(elevMaxNp-elevMin))+elevMin, elev)
# RGBAimage = tf.io.encode_png(elev)
# tf.io.write_file("elev.png", RGBAimage)