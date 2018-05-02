# rl_car_with_pymunk

Authors : LI Jiawei

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

<br><br>

Before run the code, you have to define all the parameters for the map of whole game, 
there are two ways to modify your configuration file:

* 1.Edit your own file in the root path ('rl_car_with_pymunk/'), the format json is like below:

![GitHub](https://github.com/ricarvy/rl_car_with_pymunk/blob/master/image/json_format.png "GitHub,Social Coding")

<code></code>
