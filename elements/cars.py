# -*- coding: utf-8 -*-
# __time__ = '2018/5/5 12:24'
# __author__ = 'SUN'

import pymunk
import numpy as np

from tools.distance_calculator import calculate_distance

from pygame.colordict import THECOLORS

class Car:
    def __init__(self, space, car_config):
        self.space = space
        self.car = self.create_car(space, car_config)
        self.body = self.car[0]
        self.shape = self.car[1]
        self.position = self.body.position
        self.angle= self.body.angle

    def create_car(self, space, car_configs):
        for car_config in car_configs:
            mass = car_config['mass']
            radius = car_config['radius']
            moment = pymunk.moment_for_circle(mass, 0, radius)  # 1
            body = pymunk.Body(mass, moment)  # 2
            body.position = car_config['initialize_position'][0], car_config['initialize_position'][1]  # 3
            shape = pymunk.Circle(body, radius)  # 4
            shape.color = THECOLORS[car_config['color']]
            space.add(body, shape)  # 5
        return [body, shape]

    def get_car(self):
        return self.body, self.shape


class Sensors:
    def __init__(self, space, car, carshape, config, shape):
        self.car = car
        self.carshape = carshape
        self.config = config
        self.shape = shape

        self.sensors = self.create_sensors(space)

    def add_point(self, space, x, y, color):
        mass = 1
        radius = 2
        moment = pymunk.moment_for_circle(mass, 0, radius)  # 1
        body = pymunk.Body(mass, moment)  # 2
        body.position = x, y
        shape = pymunk.Circle(body, radius)  # 4
        shape.color = THECOLORS[color]
        space.add(body, shape)  # 5
        return body, shape

    def create_arm(self, space, car, carshape, add_rate, rotation, sensor_num, deriviate_rate, color):
        car_position = car.position
        car_radius = carshape.radius
        car_angle = car.angle
        arm = []
        arm_length = 0
        for i in range(sensor_num):
            x = (
            (car_position[0] + (deriviate_rate + (i + 1) * add_rate) * car_radius * np.cos(car_angle)) - car_position[
                0])
            y = (
            (car_position[1] + (deriviate_rate + (i + 1) * add_rate) * car_radius * np.sin(car_angle)) - car_position[
                1])
            new_x = x * np.cos(rotation) - y * np.sin(rotation) + car_position[0]
            new_y = x * np.sin(rotation) + y * np.cos(rotation) + car_position[1]
            point, _ = self.add_point(space, new_x, new_y, color)
            arm.append(point)
            arm_length = calculate_distance([new_x, new_y], car_position)
        return arm, arm_length

    def create_sensors(self, space):
        car_position = self.car.position
        car_radius = self.carshape.radius
        car_angle = self.car.angle
        config = self.config
        car = self.car
        carshape = self.carshape

        sensors = []

        middle_sensor_length = -1

        if self.shape == 'trio':
            rotation = [np.pi / 4, 0, -np.pi / 4]
            middle_sensor, middle_sensor_length = self.create_arm(space, car, carshape, add_rate=config['add_rate'],
                                                             rotation=rotation[1],
                                                             sensor_num=config['sensor_num'],
                                                             deriviate_rate=config['deriviate_rate'],
                                                             color=config['color'])
            left_sensor, left_sensor_length = self.create_arm(space, car, carshape, add_rate=config['add_rate'],
                                                         rotation=rotation[0],
                                                         sensor_num=config['sensor_num'],
                                                         deriviate_rate=config['deriviate_rate'], color='pink')
            right_sensor, right_sensor_length = self.create_arm(space, car, carshape, add_rate=config['add_rate'],
                                                           rotation=rotation[2],
                                                           sensor_num=config['sensor_num'],
                                                           deriviate_rate=config['deriviate_rate'],
                                                           color=config['color'])

        sensors.append(left_sensor)
        sensors.append(middle_sensor)
        sensors.append(right_sensor)

        return sensors, middle_sensor_length

    def get_sensors(self):
        return self.sensors