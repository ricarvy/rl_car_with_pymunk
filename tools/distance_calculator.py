# -*- coding: utf-8 -*-

# @Time  :2018/5/2 13:20
# @File  : distance_calculator.py
# @Author: LI Jiawei

import numpy as np

def calculate_distance(x,y):
    return np.sqrt((x[0] - y[0])**2 + (x[1] - y[1])**2)

def calculate_angel(x,y):
    gap_x = y[0] - x[0]
    gap_y = y[1] - x[1]
    slide = (gap_x**2 + gap_y**2) ** 0.5

    if(y[0] > 0):
        return np.arccos(gap_x/slide)
    else:
        return -np.arccos(gap_x/slide)

def get_distance_level(distances):
    if distances[0] <= 0:
        return 0
    if distances[len(distances)-1] >0:
        return len(distances)
    for i in range(len(distances)):
        if i == 0:
            continue
        if distances[i-1]>0 and distances[i]<0:
            return i+1