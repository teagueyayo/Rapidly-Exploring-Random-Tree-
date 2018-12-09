# Rapidly Exploring Random Tree 

## RRT 

**rrt_planner_point_robot.py** is a RRT robot in with a point representation. The robot uniformly generates a point within the map, takes a step towards said point if there are no inteceptions between the robot's current position and the new position, and so on until the goal is reached. The idea of this program is to explore the relationship between the step sizes and the efficiency of the robot. 

A Gaussian distribution can also be used, but the **genPoint()** function needs to be edited. 

**rrt_planner_line_robot.py** is largely similar to the point robot, but the robot has a 2D representation, as well as a factor of rotation. 