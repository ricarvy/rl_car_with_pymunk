import matplotlib.pyplot as plt

x_train_frame = [2000, 5000, 10000, 20000, 50000]
y = [1100, 4658, 8321, 12049, 13657]
y_random = [694, 789, 1254, 874, 2341]

plt.plot(x_train_frame, y, 'r', label = 'train_frame')
plt.plot(x_train_frame,y_random, 'b', label = 'random ')
plt.ylabel('steps')
plt.legend(bbox_to_anchor=[0.3, 1])
plt.show()