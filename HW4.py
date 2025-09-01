import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt
xx = np.array([15, 30, 45, 60, 75], dtype=float)
yy = np.array([25, 50, 75, 100, 125], dtype=float)
sl = tf.Variable(0.0)
intc = tf.Variable(0.0)
lr = 0.01
for i in range(500):
    with tf.GradientTape() as tape:
        yp = sl * xx + intc
        loss = tf.reduce_mean((yy - yp) ** 2)
    dsl, dint = tape.gradient(loss, [sl, intc])
    sl.assign_sub(lr * dsl)
    intc.assign_sub(lr * dint)
print("m:", sl.numpy())
print("c:", intc.numpy())
p = sl.numpy() * 6 + intc.numpy()
print("x=6, y:", p)
plt.scatter(xx, yy, color="blue")
plt.plot(xx, sl.numpy() * xx + intc.numpy(), color="red")
plt.show()
