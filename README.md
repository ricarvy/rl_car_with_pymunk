# rl_car_with_pymunk

Authors : LI Jiawei，SUN Yue

## Introductions
Hello, this is the repo of Reinforcement learning with training a car to run,
avoiding the obstacles（cats and stones are included in our project, the blacks
are stones and the oranges are cats）.

### User Guid
Before runing the code ,please download the packages necessarily, the packages is
showed as below:

* keras
* tensorflow
* pymunk
* pygame
* numpy

You can use 'pip install' to build these packages. If you think that is inconvenient,
we provide repquirments,txt. You can easily use this to build your environment with
the following:

<code> pip install -r requirements.txt </code>

<br>

Before run the code, you have to define all the parameters for the map of whole game, 
there are two ways to modify your configuration file:

* 1.Edit your own file in the root path ('rl_car_with_pymunk/'), the format json is like below:

![GitHub](https://github.com/ricarvy/rl_car_with_pymunk/blob/master/image/json_format.png "json_format")

* 2.Or, we provide a convinient way if your IDE cannot show the json format normally. Please rectify
your json string in tools/json_generator.py, and use the command as below to activate the json file:

<code> cd tools </code>
<br>
<code> python json_generator.py </code>

If you see 'Done!' is output, your json file is activate.

**Hint: if you define your json file on hand, please use file name as 'config.json',other
ways are not available.**.

If you do all the above steps without errors. You can use command like
<code> python main.py --mode=example --map_random=True </code>
to start your game.The options list is showed as a doc. I will send it out later.
<br>
If you run correctly, you will see the game like below:
<br>
![GitHub](https://github.com/ricarvy/rl_car_with_pymunk/blob/master/image/game_example.png "game_example")
<br>
With the example mode(as you choose --mode=example), you can control your car (the blue circle) with 
your keyboard and mouse:

* If you click any key, the car will change it's angle and continue to run
* If you click mouse, the whole game will reset

<br>

**Continue....**

<code></code>
