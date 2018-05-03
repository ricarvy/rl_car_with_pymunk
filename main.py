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
from pymunk.vec2d import Vec2d

from argparse import ArgumentParser

import json
from tools.json_loader import config_load
from tools.distance_calculator import calculate_distance, calculate_angel
from counter.log_counter import LogCounter

from counter.experience_pool import Experience,Experience_Pool

SCREEN_HEIGHT = 600
SCREEN_WIDTH = 600
BORDER = 50
QUIT = 12
MOVE = 2
RESET = 5

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

def is_detected(space, car, car_shape, stones, stones_shape, cats, cats_shape, threshold):
    car_position = [car.position[0],car.position[1]]

    stone_positions_set = []
    for stone in stones:
        stone_positions_set.append([stone.position[0], stone.position[1]])

    for stone_position in stone_positions_set:
        distance = calculate_distance(stone_position, car_position)
        if distance <= threshold:
            print('detected! the distance is ',distance, ' , from car and stone')

    cats_position_set = []
    for cat in cats:
        cats_position_set.append([cat.position[0], cat.position[1]])

    for cat_position in cats_position_set:
        distance = calculate_distance(cat_position, car_position)
        if distance <= threshold:
            print('detected! the distance is ',distance, ' , from car and cat')
    return distance

def create_car(space, car_configs):
    for car_config in car_configs:
        mass = car_config['mass']
        radius = car_config['radius']
        moment = pymunk.moment_for_circle(mass, 0, radius)  # 1
        body = pymunk.Body(mass, moment)  # 2
        body.position = car_config['initialize_position'][0], car_config['initialize_position'][1]  # 3
        shape = pymunk.Circle(body, radius)  # 4
        shape.color = THECOLORS[car_config['color']]
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
    stones_body = []
    stones_shape = []
    for stone_config in stone_configs:
        mass = stone_config['mass']
        radius = stone_config['radius']
        moment = pymunk.moment_for_circle(mass, 0, radius)  # 1
        body = pymunk.Body(mass, moment,body_type=pymunk.Body.STATIC)  # 2
        body.position = stone_config['initialize_position'][0], stone_config['initialize_position'][1]  # 3
        shape = pymunk.Circle(body, radius)  # 4
        shape.color = THECOLORS[stone_config['color']]
        space.add(body, shape)  # 5
        stones_body.append(body)
        stones_shape.append(shape)
    return stones_body, stones_shape

def create_random_stones(space, stones_num):
    stones_body = []
    stones_shape = []
    for index in range(stones_num):
        mass = np.random.randint(10,50)
        radius = np.random.randint(20,50)
        moment = pymunk.moment_for_circle(mass, 0, radius)  # 1
        body = pymunk.Body(mass, moment,body_type=pymunk.Body.STATIC)  # 2
        body.position = np.random.randint(100,500), np.random.randint(100,500)
        shape = pymunk.Circle(body, radius)  # 4
        shape.color = THECOLORS['black']
        space.add(body, shape)  # 5
        stones_body.append(body)
        stones_shape.append(shape)
    return stones_body, stones_shape

def create_random_cats(space, cats_num):
    cats_body = []
    cats_shape = []
    for cat_config in range(cats_num):
        mass = 1
        radius = 10
        moment = pymunk.moment_for_circle(mass, 0, radius)  # 1
        body = pymunk.Body(mass, moment)  # 2
        body.position = np.random.randint(100,500), np.random.randint(100, 500)  # 3
        shape = pymunk.Circle(body, radius)  # 4
        shape.color = THECOLORS['orange']
        space.add(body, shape)  # 5
        cats_body.append(body)
        cats_shape.append(shape)
    return cats_body, cats_shape

def create_cats(space, cat_configs):
    cats_body = []
    cats_shape = []
    for cat_config in cat_configs:
        mass = cat_config['mass']
        radius = cat_config['radius']
        moment = pymunk.moment_for_circle(mass, 0, radius)  # 1
        body = pymunk.Body(mass, moment)  # 2
        body.position = cat_config['initialize_position'][0], cat_config['initialize_position'][1]  # 3
        shape = pymunk.Circle(body, radius)  # 4
        shape.color = THECOLORS[cat_config['color']]
        space.add(body, shape)  # 5
        cats_body.append(body)
        cats_shape.append(shape)
    return cats_body, cats_shape

def add_point(space,x,y,color):
    mass = 1
    radius = 2
    moment = pymunk.moment_for_circle(mass, 0, radius) # 1
    body = pymunk.Body(mass, moment) # 2
    body.position = x, y
    shape = pymunk.Circle(body, radius) # 4
    shape.color = THECOLORS[color]
    space.add(body, shape) # 5
    return body, shape

def create_arm(space, car, carshape, add_rate, rotation,sensor_num, deriviate_rate, color):
    car_position = car.position
    car_radius = carshape.radius
    car_angle = car.angle
    arm = []
    arm_length = 0
    for i in range(sensor_num):
        x = ((car_position[0] + (deriviate_rate + (i + 1) * add_rate) * car_radius * np.cos(car_angle)) - car_position[0])
        y = ((car_position[1] + (deriviate_rate + (i + 1) * add_rate) * car_radius * np.sin(car_angle)) - car_position[1])
        new_x = x * np.cos(rotation) - y * np.sin(rotation) + car_position[0]
        new_y = x * np.sin(rotation) + y * np.cos(rotation) + car_position[1]
        point, _ = add_point(space, new_x, new_y, color)
        arm.append(point)
        arm_length = calculate_distance([new_x, new_y], car_position)
    return arm, arm_length

def create_sensors(space, car, carshape, config, shape='trio'):
    car_position = car.position
    car_radius = carshape.radius
    car_angle = car.angle

    sensors = []

    middle_sensor_length = -1

    if shape == 'trio':
        rotation = [np.pi/4, 0, -np.pi/4]
        middle_sensor, middle_sensor_length = create_arm(space,car,carshape,add_rate=config['add_rate'], rotation = rotation[1],
                                   sensor_num=config['sensor_num'], deriviate_rate=config['deriviate_rate'], color = config['color'])
        left_sensor, left_sensor_length = create_arm(space,car,carshape,add_rate=config['add_rate'], rotation = rotation[0],
                                   sensor_num=config['sensor_num'], deriviate_rate=config['deriviate_rate'], color = 'pink')
        right_sensor, right_sensor_length = create_arm(space,car,carshape,add_rate=config['add_rate'], rotation = rotation[2],
                                   sensor_num=config['sensor_num'], deriviate_rate=config['deriviate_rate'], color = config['color'])

    sensors.append(left_sensor)
    sensors.append(middle_sensor)
    sensors.append(right_sensor)

    return sensors, middle_sensor_length

def sensors_rectify(space, car, carshape, sensors, rotation,add_rate):
    car_position = car.position
    car_angle = car.angle
    car_radius = carshape.radius

    for k,sensor in enumerate(sensors):
        for i,point in enumerate(sensor):
            x = ((car_position[0] + (0.5 + (i + 1) * add_rate) * car_radius * np.cos(car_angle)) - car_position[0])
            y = ((car_position[1] + (0.5 + (i + 1) * add_rate) * car_radius * np.sin(car_angle)) - car_position[1])
            new_x = x * np.cos(rotation[k]) - y * np.sin(rotation[k]) + car_position[0]
            new_y = x * np.sin(rotation[k]) + y * np.cos(rotation[k]) + car_position[1]
            point.position = new_x,new_y

def car_angel_changed(car, changed_angle, sensors):
    car.angle += (changed_angle)
    for sensor in sensors:
        for arm in sensor:
            # new_x = ((car.position[0] - sensor.position[0]) * np.cos(np.pi / 4) + (
            # car.position[1] - sensor.position[1]) * np.sin(np.pi / 4)) + sensor.position[0]
            # new_y = 600-(((sensor.position[1] - car.position[1]) * np.sin(np.pi / 4) - (
            # sensor.position[0] - car.position[0]) * np.cos(np.pi / 4)) + sensor.position[1])

            # new_x = ((sensor.position[0] - car.position[0]) * np.cos(np.pi / 4) - (
            # sensor.position[1] - car.position[1]) * np.sin(np.pi / 4)) + car.position[0]
            # new_y = 600-(((car.position[1] - sensor.position[1]) * np.sin(np.pi / 4) + (
            # car.position[0] - sensor.position[0]) * np.cos(np.pi / 4)) + car.position[1])

            new_x = ((arm.position[0] - car.position[0]) * np.cos(changed_angle) - (
            arm.position[1] - car.position[1]) * np.sin(
                changed_angle)) + car.position[0]
            new_y = ((arm.position[0] - car.position[0]) * np.sin(changed_angle) + (
            arm.position[1] - car.position[1]) * np.cos(
                changed_angle)) + car.position[1]
            arm.position = new_x, new_y

def cats_move(cats, log_counter):
    ### cat moving
    cats.position = cats.position[0] + 2 * np.cos(cats.angle), \
                    cats.position[1] + 2 * np.sin(cats.angle)
    if (log_counter.step_count % 50 == 0):
        cats_changed_angle = np.random.randint(-1, 2) * (np.pi / 4)
        cats.angle += cats_changed_angle
    if (cats.position[0] < BORDER or cats.position[0] > SCREEN_WIDTH - BORDER) or (
            cats.position[1] < BORDER or cats.position[1] > SCREEN_HEIGHT - BORDER):
        cats.angle += np.pi

def car_move(car, sensors, speed):
    car.position = car.position[0] + speed * np.cos(car.angle), car.position[1] + speed * np.sin(car.angle)
    for sensor in sensors:
        for point in sensor:
            point.position = point.position[0] + speed * np.cos(car.angle), point.position[1] + speed * np.sin(car.angle)

def reset_game(map_random, space, car, carshape, sensors,arm_shape = 'trio'):
    create_an_expmple(map_random, config_load(), LogCounter())
    sys.exit(0)

def get_distance_level(distances, sensor_length):
    if distances[0] <= 0:
        return 0
    if distances[len(distances)-1] >0:
        return len(distances)
    for i in range(len(distances)):
        if i == 0:
            continue
        if distances[i-1]>0 and distances[i]<0:
            return i+1

def get_reading(car, car_shape, sensors, sensor_length, stones, stones_shape, cats, cats_shape):
    car_position = car.position
    car_angle = car.angle
    reading = []
    for i,sensor in enumerate(sensors):
        distances=[]
        for p,point in enumerate(sensor):
            stone_distance = 9999999
            for s,stone in enumerate(stones):
                distance = calculate_distance(point.position, stone.position) - stones_shape[s].radius
                if stone_distance > distance:
                    stone_distance = distance

            for c,cat in enumerate(cats):
                distance = calculate_distance(point.position, cat.position) - stones_shape[c].radius
                if stone_distance > distance:
                    stone_distance = distance

            distances.append(stone_distance)
            distance_level = get_distance_level(distances, sensor_length)
        reading.append(distance_level)
    print(reading)


    return reading

def create_an_expmple(map_random, config, log_counter):
    crashed = False
    ep = Experience_Pool()

    pygame.init()
    screen = pygame.display.set_mode((SCREEN_HEIGHT, SCREEN_WIDTH))
    pygame.draw.circle(screen, (255, 255, 255), (300,300), 2)
    pygame.display.set_caption('Reinforcement Learning Game')
    clock = pygame.time.Clock()

    space = pymunk.Space()
    space.gravity = (0.0, 0.0)
    draw_options = DrawOptions(screen)

    ### create the world map
    ### create the car
    car, carshape = create_car(space, config['cars'])
    sensors, sensor_length = create_sensors(space,car,carshape,config['sensors'][0] ,'trio')

    if map_random == False:
        ### create walls
        # walls = create_walls(space, config['walls'])
        ### create stones
        stones, stones_shape = create_stones(space, config['stones'])
        ### create cats
        cats, cats_shape = create_cats(space, config['cats'])
    else:
        stones,stones_shape = create_random_stones(space, 3)
        cats, cats_shape = create_random_cats(space, 2)

    ### initialize old_State
    old_state = Vec2d(BORDER, BORDER)
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                sys.exit(0)
            elif event.type == MOVE:
                car_angel_changed(car,np.pi/4,sensors)

            elif event.type == RESET:
                reset_game(map_random, space, car, sensors, np.pi/4)
        car_move(car, sensors, 3)
        for cat in cats:
            cats_move(cat,log_counter)

        reading = get_reading(car,carshape,sensors,sensor_length,stones,stones_shape, cats, cats_shape)

        if (0 in reading):
            reset_game(map_random,space,car,carshape,sensors,'trio')

        # is_detected(space,car,carshape,stones,stones_shape,cats,cats_shape,100)
        sensors_rectify(space,car,carshape,sensors,[np.pi/4,0,-np.pi/4],1)

        if (car.position[0] < BORDER-5 or car.position[0] > SCREEN_WIDTH-BORDER+5 ) or (car.position[1] < BORDER-5 or car.position[1] >SCREEN_HEIGHT-BORDER+5):
            car_angel_changed(car, np.pi / 2, sensors)

        space.step(1 / 50.0)

        screen.fill(THECOLORS['whitesmoke'])
        space.debug_draw(draw_options)

        pygame.display.flip()
        clock.tick(50)


        new_state = old_state

        if log_counter.step_count % 100 == 0:
            new_state = car.position
            action = car.angle
            reward = 50
            experience = Experience(old_state,action,new_state,reward)
            ep.experienct_pool.append(experience)
            old_state = new_state
            # ep.show_all()
        log_counter.step_count += 1

def main():
    config = config_load()
    log_counter = LogCounter()

    parser = build_paser()
    options = parser.parse_args()
    map_random = options.map_random
    if options.mode == 'example':
        create_an_expmple(map_random, config, log_counter)



if __name__ == '__main__':
    main()
