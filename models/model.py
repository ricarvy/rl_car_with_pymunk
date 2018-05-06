# -*- coding: utf-8 -*-

# @Time  :2018/5/4 13:17
# @File  : models.py
# @Author: LI Jiawei

from keras.models import Sequential
from keras.layers.core import Dense, Activation, Dropout
from keras.optimizers import RMSprop
from keras.layers.recurrent import LSTM
from keras.callbacks import Callback
from keras.utils import plot_model
from keras.models import load_model
import numpy as np

import datetime

class Model:
    def __init__(self, num_sensors, params, load=''):

        self.model = self.build_model(num_sensors,params,load)

    def build_model(self,num_sensors, params, load=''):
        model = Sequential()

        # First layer.
        model.add(Dense(
            params[0], kernel_initializer='lecun_uniform', input_shape=(num_sensors,)
        ))
        model.add(Activation('relu'))
        model.add(Dropout(0.2))

        # Second layer.
        model.add(Dense(params[1], kernel_initializer='lecun_uniform'))
        model.add(Activation('relu'))
        model.add(Dropout(0.2))

        # Output layer.
        model.add(Dense(3, kernel_initializer='lecun_uniform'))
        model.add(Activation('linear'))

        rms = RMSprop()
        model.compile(loss='mse', optimizer=rms)

        if load:
            model.load_weights(load)
        return model

    def get_summary(self):
        return self.model.summary()

    def predict(self, X, batch_size=1):
        result = self.model.predict(X, batch_size)
        return result

    ### error
    def plot_model(self, to_file, show_shapes = True, show_layer_names = True):
        plot_model(self.model,to_file,show_shapes,show_layer_names)

    def save_model(self):
        current = datetime.datetime.now()
        time_str = str(current.day) + '-' + str(current.month) + '-' + str(current.year) + '-' + str(
            current.hour) + ':' + str(current.minute) + ':' + str(current.second)
        filepath = 'original_model_%s.h5' % time_str
        self.model.save('models/oringin_model_%s.h5' % filepath)

def load():
    model = load_model('oringin_model_%s.h5')
    return model


# NUM_INPUT = 3
# nn_param = [128, 128]
# params = {
#     "batchSize": 64,
#     "buffer": 50000,
#     "nn": nn_param
# }
# model = Model(NUM_INPUT,params['nn'])
# X = np.array([5,5,5]).reshape((1,3))
# # y = np.array(np.arange(0,15).reshape(5,3))
# result = model.model.predict(X)
# print(result)
# model.plot_model('model.png')

# model = load()
# test_data = np.array([5,5,5]).reshape((1,3))
# result = model.predict(test_data)
# print(result)
