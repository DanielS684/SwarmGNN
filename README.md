# SwarmNet
This is my first github project just seeing how stuff work.

This project is going to try and control a swarm of robots (balls) by changing their electric charge.

I'm using a neural network for controlling the coefficients a formula to determine the charge of a ball.

I got this idea from the algorithm game of life and thought that if I could use a polynomial function to determine the charges of an object dyynamically then it could make swarm robotics dynamic and easy.

Several problems occurred during making this project such as incorrect data, bugs in the simulation that the neural network would exploit, and multiple failures on actually building and training the network since these things are very fragile.

Since I wanted to be able to form a shape anywhere on the board independent of rotation I came up with a way to determine that through measuring the average distance between all the other balls and did that for every ball, since those sets of averages are unique for every shape.

The ChargeNet.tar file contains the weights for the neural network, the epoch it was on when chosen, and the optimizer configurations

The 680912_1195657_compressed_replay_buffer.npy.zip file contains the data I collected to train the neural network. The way I gathered the data was through assigning random action coefficients and seeing what states would occur after a minute of playing it out (I collected 3,000 examples). Then just passing the states to the ChargeNet and make it try and find what action coefficients made that state.

A few things I would change about this project would be to make it possible to pass in the beginning state of the board as well as the end state so I could do it from any starting position. Another thing that I would change is the fact that right now a specific ball would need to be in a specific place for it to count so I would want to try and make it possible so that any ball could take that position and if any balls were missing it would still form the general shape.

Inspirations for this work include the following:

https://arxiv.org/pdf/1912.02877.pdf

https://distill.pub/2020/growing-ca/

https://en.wikipedia.org/wiki/Conway%27s_Game_of_Life

PS. Also for funsies I listen to podcasts from this person called Lex Fridman and he does amazing interviews on AI, physics, etc.
You can find his AI series here: https://www.youtube.com/user/lexfridman/playlists
