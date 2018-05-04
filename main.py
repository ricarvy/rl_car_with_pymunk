# -*- coding: utf-8 -*-

# @Time  :2018/4/30 13:46
# @File  : main.py
# @Author: LI Jiawei

import sys
import pygame
from pygame.locals import *
import pymunk #1
import numpy as np
import timeit
import random
from pymunk.pygame_util import DrawOptions
from pygame.colordict import THECOLORS
from pymunk.vec2d import Vec2d
from keras.callbacks import Callback

from argparse import ArgumentParser

import json
from tools.json_loader import config_load
from tools.distance_calculator import calculate_distance, calculate_angel
from counter.log_counter import LogCounter
from models.model import Model

from counter.experience_pool import Experience,Experience_Pool

SCREEN_HEIGHT =600
SCREEN_WIDTH = 600
BORDER = 50
QUIT = 12
MOVE = 2
RESET = 5
IS_CRASHED = False
OBSERVE = 100
NUM_INPUT = 3
GAMMA = 0.9
TRAIN_FRAMES = 100000

class LossHistory(Callback):
    def on_train_begin(self, logs={}):
        self.losses = []

    def on_batch_end(self, batch, logs={}):
        self.losses.append(logs.get('loss'))

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

def reset_game(map_random, space, car, carshape, sensors,log_counter,ep,model,arm_shape = 'trio'):
    create_an_expmple(map_random, config_load(), log_counter, ep, model)
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

def get_readings(car, car_shape, sensors, sensor_length, stones, stones_shape, cats, cats_shape):
    car_position = car.position
    car_angle = car.angle
    reading = []
    if (car.position[0] < BORDER - 5 or car.position[0] > SCREEN_WIDTH - BORDER + 5) or (
            car.position[1] < BORDER - 5 or car.position[1] > SCREEN_HEIGHT - BORDER + 5):
        return [0,0,0]
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

    return reading

def get_reward_and_new_state(action, readings, car, carshape, sensors, sensor_length, stones, stones_shape, cats, cats_shape):
    state = readings
    # normalized_readings = [(x - sensor_length / 2) / sensor_length for x in readings]
    # state = np.array([normalized_readings])

    ### Set the reward
    ### Car crashed when any reading == 0
    reward = 0
    if (0 in readings):
        IS_CRASHED = True
        reward = -500
    else:
        # Higher readings are better, so return the sum
        reward = -5 + int(np.sum(readings))

    return reward, state

def process_minibatch2(minibatch, model):
    # by Microos, improve this batch processing function
    #   and gain 50~60x faster speed (tested on GTX 1080)
    #   significantly increase the training FPS

    # instead of feeding data to the model one by one,
    #   feed the whole batch is much more efficient

    mb_len = len(minibatch)

    old_states = np.zeros(shape=(mb_len, 3))
    actions = np.zeros(shape=(mb_len,))
    rewards = np.zeros(shape=(mb_len,))
    new_states = np.zeros(shape=(mb_len, 3))

    for i, m in enumerate(minibatch):
        old_state_m, action_m, reward_m, new_state_m = m
        old_states[i, :] = old_state_m[...]
        actions[i] = action_m
        rewards[i] = reward_m
        new_states[i, :] = new_state_m[...]

    old_qvals = model.predict(np.array(old_states), batch_size=mb_len)
    new_qvals = model.predict(np.array(new_states), batch_size=mb_len)

    maxQs = np.max(new_qvals, axis=1)
    y = old_qvals
    non_term_inds = np.where(rewards != -500)[0]
    term_inds = np.where(rewards == -500)[0]

    y[non_term_inds, actions[non_term_inds].astype(int)] = rewards[non_term_inds] + (GAMMA * maxQs[non_term_inds])
    y[term_inds, actions[term_inds].astype(int)] = rewards[term_inds]

    X_train = old_states
    y_train = y
    return X_train, y_train

def process_minibatch(minibatch, model):
    """This does the heavy lifting, aka, the training. It's super jacked."""
    X_train = []
    y_train = []
    # Loop through our batch and create arrays for X and y
    # so that we can fit our model at every step.
    for memory in minibatch:
        # Get stored values.
        old_state_m, action_m, reward_m, new_state_m = memory
        # print('old_state_m ',np.array(old_state_m).reshape((3,)).shape)
        # Get prediction on old state.
        old_qval = model.predict(np.array(old_state_m).reshape((3,1)), batch_size=1)
        # Get prediction on new state.
        newQ = model.predict(np.array(new_state_m), batch_size=1)
        # Get our predicted best move.
        maxQ = np.max(newQ)
        y = np.zeros((1, 3))
        y[:] = old_qval[:]
        # Check for terminal state.
        if reward_m != -500:  # non-terminal state
            update = (reward_m + (GAMMA * maxQ))
        else:  # terminal state
            update = reward_m
        # Update the value for the action we took.
        y[0][action_m] = update
        X_train.append(old_state_m.reshape(NUM_INPUT,))
        y_train.append(y.reshape(3,))

    X_train = np.array(X_train)
    y_train = np.array(y_train)

    return X_train, y_train

def create_an_expmple(map_random, config, log_counter,ep, model):
    crashed = False
    epsilon = 1
    loss_log = []
    car_distance = 0
    max_car_distance = 0
    data_collect = []
    rotation_rate = config['cars'][0]['rotation']
    nn_param = [128, 128]
    params = {
        "batchSize": 64,
        "buffer": 50000,
        "nn": nn_param
    }


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
    sensors, sensor_length = create_sensors(space,car,carshape,config['sensors'][0], 'trio')

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

    ### initialize the state
    readings = get_readings(car, carshape, sensors, sensor_length, stones, stones_shape, cats, cats_shape)
    start_time = timeit.default_timer()
    _, state = get_reward_and_new_state(2, readings, car, carshape, sensors, sensor_length, stones, stones_shape, cats, cats_shape)

    while log_counter.step_count < TRAIN_FRAMES:
        log_counter.step_count += 1
        car_distance += 1

        for event in pygame.event.get():
            if event.type == QUIT:
                sys.exit(0)
            elif event.type == MOVE:
                car_angel_changed(car,rotation_rate,sensors)

            elif event.type == RESET:
                reset_game(map_random, space, car, sensors, log_counter, ep, model)
        car_move(car, sensors, 3)
        for cat in cats:
            cats_move(cat,log_counter)

        readings = get_readings(car, carshape, sensors, sensor_length, stones, stones_shape, cats, cats_shape)
        ### choose action
        if np.random.random() < epsilon or log_counter < OBSERVE:
            action = np.random.randint(0, 3)
        else:
            qval = model.predict(state,batch_size = 1)
            action = (np.argmax(qval))
        if action == 0:
            car_angel_changed(car, rotation_rate, sensors)
        elif action ==1:
            car_angel_changed(car, -rotation_rate, sensors)
        reward, new_state = get_reward_and_new_state(action,readings,car, carshape, sensors, sensor_length, stones, stones_shape, cats, cats_shape)
        ep.experienct_pool.append((state, action, reward, new_state))

        if log_counter.step_count > OBSERVE:

            if ep.get_experiece_pool_length() > params['buffer']:
                ep.pop_old_experience()

            minibatch = random.sample(ep.experienct_pool, params['batchSize'])


            ### Prepare for train and test data
            X_train, y_train = process_minibatch(minibatch, model)

            history = LossHistory()
            model.fit(X_train, y_train, params['batchSize'],nb_epoch = 1, verbose = 0, callbacks = [history])

            loss_log.append(history.losses)

        state = new_state

        ### reduce the value of epsilon
        if epsilon > 0.1 and log_counter.step_count > OBSERVE:
            epsilon -= (1.0 / TRAIN_FRAMES)

        ### record the information of one game
        ### one game over !
        if reward == -500:
            data_collect.append([log_counter.step_count, car_distance])

            ### update max car distance
            if car_distance > max_car_distance:
                max_car_distance = car_distance

            total_time = timeit.default_timer() - start_time
            fps = car_distance / total_time

            print("Max: %d at %d\tepsilon %f\t(%d)\t%f fps" %
                (max_car_distance, log_counter.step_count, epsilon, car_distance, fps))

            # Reset.
            car_distance = 0
            start_time = timeit.default_timer()

        if (0 in readings):
            reset_game(map_random,space,car,carshape,sensors,log_counter, ep, model)

        # is_detected(space,car,carshape,stones,stones_shape,cats,cats_shape,100)
        sensors_rectify(space,car,carshape,sensors,[np.pi/4,0,-np.pi/4],1)


        space.step(1 / 50.0)

        screen.fill(THECOLORS['whitesmoke'])
        space.debug_draw(draw_options)

        pygame.display.flip()
        clock.tick(50)


def main():
    config = config_load()
    log_counter = LogCounter()
    ep = Experience_Pool()
    parser = build_paser()
    options = parser.parse_args()
    map_random = options.map_random

    ### model builder
    nn_param = [128, 128]
    params = {
        "batchSize": 64,
        "buffer": 50000,
        "nn": nn_param
    }
    model = Model(NUM_INPUT, params['nn'])
    model.get_summary()

    if options.mode == 'example':
        create_an_expmple(map_random, config, log_counter, ep, model)



if __name__ == '__main__':
    main()
