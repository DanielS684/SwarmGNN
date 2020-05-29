# SwarmNet
This is my first github project just seeing how stuff work.

This project is going to try and control a swarm of robots (balls) by changing their electric charge.

I'm using a neural network for controlling the coefficients a formula to determine the charge of a ball.

I got this idea from the algorithm game of life and thought that if I could use a polynomial function to determine the charges of an object dyynamically then it could make swarm robotics dynamic and easy.

Several problems occurred during making this project such as incorrect data, bugs in the simulation that the neural network would exploit, and multiple failures on actually building and training the network since these things are very fragile.

Since I wanted to be able to form a shape anywhere on the board in any rotation I came up with a way to determine that through measuring the average distance between all the other balls and did that for every ball, since those sets of averages are unique for every shape.

