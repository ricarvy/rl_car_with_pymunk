# -*- coding: utf-8 -*-

# @Time  :2018/4/30 13:44
# @File  : test.py
# @Author: LI Jiawei

import sys
import pygame
from pygame.locals import *
import pymunk #1
import numpy as np
from pymunk.pygame_util import DrawOptions


QUIT = 12
MOVE = 2

def add_ball(space):
    mass = 1
    radius = 14
    moment = pymunk.moment_for_circle(mass, 0, radius) # 1
    body = pymunk.Body(mass, moment) # 2
    x = np.random.randint(120, 380)
    body.position = x, -500 # 3
    shape = pymunk.Circle(body, radius) # 4
    space.add(body, shape) # 5
    return body, shape

def main():
    pygame.init()
    screen = pygame.display.set_mode((600, 600))
    pygame.display.set_caption("Joints. Just wait and the L will tip over")
    clock = pygame.time.Clock()

    space = pymunk.Space()
    space.gravity = (0.0, 0.0)

    balls = []
    draw_options = DrawOptions(screen)

    ball, ball_shape = add_ball(space)


    ticks_to_next_ball = 10
    while True:
        for event in pygame.event.get():
            # print(event.type)
            if event.type == QUIT:
                sys.exit(0)
            elif event.type == MOVE:
                ball.angle += (np.pi/4)
        ball.position = ball.position[0] + 2*np.cos(ball.angle) , ball.position[1] + 2*np.sin(ball.angle)


        # ticks_to_next_ball -= 1
        # if ticks_to_next_ball <= 0:
        #     ticks_to_next_ball = 25
        #     ball_shape = add_ball(space)
        #     balls.append(ball_shape)

        space.step(1/50.0)

        screen.fill((0,0,0))
        space.debug_draw(draw_options)

        pygame.display.flip()
        clock.tick(50)

if __name__ == '__main__':
    main()
