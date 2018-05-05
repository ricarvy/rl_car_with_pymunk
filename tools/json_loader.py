# -*- coding: utf-8 -*-

# @Time  :2018/4/30 16:49
# @File  : json_loader.py
# @Author: LI Jiawei

import json

path = 'config.json'

def config_load():
    with open(path, 'r') as file:
        return json.load(file)

config_load()