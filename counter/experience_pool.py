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

    def show_all(self):
        print('\nCurrent Experiece Pool:/n Length : ',len(self.experienct_pool))
        for experience in self.experienct_pool:
            print('Old state: ', experience.old_state,
                  '   action: ' , experience.action,
                  '   reward: ',experience.reward,
                  '   new_state: ',experience.new_state,)

    def get_experiece_pool_length(self):
        return len(self.experienct_pool)

    def pop_old_experience(self):
        self.experienct_pool.pop(0)