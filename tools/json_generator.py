# -*- coding: utf-8 -*-

# @Time  :2018/4/30 16:27
# @File  : json_generator.py
# @Author: LI Jiawei

import json

BORDER = 200

dict = {
    'cars':
        [
            {
                'initialize_position' : [500,100],
                'mass' : 10,
                'radius' : 15,
                'color' : 'yellowgreen',
                'rotation' : .2,
             }
        ],
    'walls':
        [
            {
                'initialize_position' : [300, 300],
                'start_endpoint' : [0, -75],
                'end_endpoint' : [0, 75],
                'radius' : 1
            },
            {
                'initialize_position' : [100, 100],
                'start_endpoint' : [0, -75],
                'end_endpoint' : [0, 75],
                'radius' : 1
            }
        ],

    'stones':
        [
            {
                'initialize_position': [300, 400],
                'mass': 10,
                'radius': 90,
                'color': 'black'
            },
            {
                'initialize_position': [750, 250],
                'mass': 10,
                'radius': 60,
                'color': 'black'
            }
        ],

    'cats':
        [
            {
                'initialize_position' : [100, 500],
                'mass' : 1,
                'radius' : 15,
                'color' : 'orange'
            }
        ],

    'sensors':
        [
            {
                'sensor_num' : 7,
                'deriviate_rate' : 0.5,
                'add_rate' : 1,
                'color' : 'black'
            }
        ]
}

with open('config.json', 'w') as file:
    json.dump(dict, file)
    print('Done!')