# -*- coding: utf-8 -*-

# @Time  :2018/4/30 13:46
# @File  : main.py
# @Author: LI Jiawei

import sys
import pygame
from pygame.locals import *
import pymunk #1
import numpy as np
from pymunk.pygame_util import DrawOptions
from pygame.colordict import THECOLORS

from argparse import ArgumentParser

import json
from tools.json_loader import config_load

SCREEN_HEIGHT = 600
SCREEN_WIDTH = 600
BORDER = 50
QUIT = 12
MOVE = 2

def build_paser():
    parser = ArgumentParser()
    parser.add_argument('--mode',dest='mode')

    parser.add_argument('--map_random',
                        dest='map_random',
                        help = 'Using map from config or using random map, default is False',
                        default=False)

    return parser

def add_ball(space):
    mass = 1
    radius = 14
    moment = pymunk.moment_for_circle(mass, 0, radius) # 1
    body = pymunk.Body(mass, moment) # 2
    x = np.random.randint(120, 380)
    body.position = x, 550 # 3
    shape = pymunk.Circle(body, radius) # 4
    space.add(body, shape) # 5
    return body, shape

def create_car(space, car_configs):
    for car_config in car_configs:
        mass = car_config['mass']
        radius = car_config['radius']
        moment = pymunk.moment_for_circle(mass, 0, radius)  # 1
        body = pymunk.Body(mass, moment)  # 2
        body.position = car_config['initialize_position'][0], car_config['initialize_position'][1]  # 3
        shape = pymunk.Circle(body, radius)  # 4
        space.add(body, shape)  # 5
    return body, shape

def create_walls(space, wall_configs):
    for wall_config in wall_configs:
        body = pymunk.Body(body_type=pymunk.Body.STATIC)
        body.position = (wall_config['initialize_position'][0], wall_config['initialize_position'][1])
        l = pymunk.Segment(body,
                           (wall_config['start_endpoint'][0], wall_config['start_endpoint'][1]),
                           (wall_config['end_endpoint'][0],wall_config['end_endpoint'][1]),
                           wall_config['radius'])
        space.add(l)
    return l

def create_stones(space, stone_configs):
    for stone_config in stone_configs:
        mass = stone_config['mass']
        moment = pymunk.moment_for_box(mass, (stone_config['moment'][0], stone_config['moment'][1]))
        body = pymunk.Body(mass,moment)
        body.position = stone_config['initialize_position'][0], stone_config['initialize_position'][1]
        shape = pymunk.Poly.create_box(body, (stone_config['size'][0],stone_config['size'][1]), stone_config['inner_radius'])
        shape.color = THECOLORS[stone_config['color']]
        space.add(body, shape)
    return body,shape

def create_cats(space, cat_configs):
    for cat_config in cat_configs:
        mass = cat_config['mass']
        radius = cat_config['radius']
        moment = pymunk.moment_for_circle(mass, 0, radius)  # 1
        body = pymunk.Body(mass, moment)  # 2
        body.position = cat_config['initialize_position'][0], cat_config['initialize_position'][1]  # 3
        shape = pymunk.Circle(body, radius)  # 4
        shape.color = THECOLORS[cat_config['color']]
        space.add(body, shape)  # 5
    return body, shape

def create_an_expmple(map_random, config):
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_HEIGHT, SCREEN_WIDTH))
    pygame.display.set_caption("Joints. Just wait and the L will tip over")
    clock = pygame.time.Clock()

    space = pymunk.Space()
    space.gravity = (0.0, 0.0)
    draw_options = DrawOptions(screen)

    ### create the world map
    ### create the car
    car, carshape = create_car(space, config['cars'])

    ### create walls
    walls = create_walls(space, config['walls'])
    ### create stones
    stones, stones_shape = create_stones(space, config['stones'])
    ### create cats
    cats, cats_shape = create_cats(space, config['cats'])

    tick_to_change_cat_ango = 0
    while True:
        for event in pygame.event.get():
            # print(event.type)
            if event.type == QUIT:
                sys.exit(0)
            elif event.type == MOVE:
                car.angle += (np.pi / 4)
        car.position = car.position[0] + 2 * np.cos(car.angle), car.position[1] + 2 * np.sin(car.angle)
        if (car.position[0] <= BORDER or car.position[0] >= SCREEN_WIDTH-BORDER ) or (car.position[1] <= BORDER or car.position[1] >=SCREEN_HEIGHT-BORDER):
            car.angle += np.pi/2

        ### cat moving
        tick_to_change_cat_ango += 1
        cats.position = cats.position[0] + 2 * np.cos(cats.angle), \
                        cats.position[1] + 2 * np.sin(cats.angle)
        if(tick_to_change_cat_ango == 50):
            cats_changed_angle = np.random.randint(-1,2) * (np.pi / 4)
            cats.angle += cats_changed_angle
            tick_to_change_cat_ango = 0
        if (cats.position[0] <= BORDER or cats.position[0] >= SCREEN_WIDTH-BORDER ) or (cats.position[1] <= BORDER or cats.position[1] >=SCREEN_HEIGHT-BORDER):
            cats.angle += np.pi/2

        space.step(1 / 50.0)

        screen.fill((245, 245, 245))
        space.debug_draw(draw_options)

        pygame.display.flip()
        clock.tick(50)

def main():
    config = config_load()
    parser = build_paser()
    options = parser.parse_args()
    map_random = options.map_random
    if options.mode == 'example':
        create_an_expmple(map_random, config)



if __name__ == '__main__':
    main()
