# -*- coding: utf-8 -*-

# @Time  :2018/5/4 13:17
# @File  : models.py
# @Author: LI Jiawei

from keras.models import Sequential
from keras.layers.core import Dense, Activation, Dropout
from keras.optimizers import RMSprop
from keras.layers.recurrent import LSTM
from keras.callbacks import Callback
import numpy as np


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
        self.model.predict(X, batch_size)

NUM_INPUT = 3
nn_param = [128, 128]
params = {
    "batchSize": 64,
    "buffer": 50000,
    "nn": nn_param
}
model = Model(NUM_INPUT,params['nn'])
