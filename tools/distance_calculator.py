# -*- coding: utf-8 -*-

# @Time  :2018/5/2 13:20
# @File  : distance_calculator.py
# @Author: LI Jiawei

import numpy as np

def calculate_distance(x,y):
    return np.sqrt((x[0] - y[0])**2 + (x[1] - y[1])**2)