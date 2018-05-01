# -*- coding: utf-8 -*-

# @Time  :2018/5/1 18:36
# @File  : experience_pool.py
# @Author: LI Jiawei

class Experience:

    def __init__(self, old_state, action, new_State, reward):
        self.old_state = old_state

        self.action = action

        self.reward = reward

        self.new_state = new_State

class Experience_Pool:

    def __init__(self):

        self.experienct_pool = []

        self.limitation = 10000

