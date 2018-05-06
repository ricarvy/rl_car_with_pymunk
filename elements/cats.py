# -*- coding: utf-8 -*-
# __time__ = '2018/5/6 10:08'
# __author__ = 'SUN'

import pymunk

from pygame.colordict import THECOLORS

class Cat:

    def __init__(self, space, config):
        self.bodies, self.shapes = self.create_cats()
        self.position = self.create_cats_position()
        self.angles = self.create_cats_angle()
        self.config = config

    def create_cats(self, space):
        cats_body = []
        cats_shape = []
        for cat_config in self.config:
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

    def create_cats_position(self):
        positions = []
        for body in self.bodies:
            positions.append(body.position)
        return positions

    def create_cats_angle(self):
        angles = []
        for body in self.bodies:
            angles.append(body.angle)
        return angles