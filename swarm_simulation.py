import pygame, math
from random import randint, uniform, sample, shuffle
import torch
from torch import nn
import torch.nn.functional as F
import numpy as np
from tqdm import tqdm


pygame.init()
clock = pygame.time.Clock()

screen_width = 1000
screen_height = 700
friction = 0.9999
elasticity = 0.87
player_colors = ["green" if a < 10 else "maroon" if a >= 10 else None for a in range(20)]

class chargeNet(nn.Module):
    def __init__(self):
        super().__init__()
        self.layer1 = nn.Linear(20,160)
        self.layer2 = nn.Linear(160, 128)
        self.layer3 = nn.Linear(128, 96)
        self.layer4 = nn.Linear(96,64)
        self.layer5 = nn.Linear(64,32)

    def forward(self, state):
        state = state.view(state.shape[0],-1)
        x = F.relu(self.layer1(state))
        x = F.relu(self.layer2(x))
        x = F.relu(self.layer3(x))
        x = F.relu(self.layer4(x))
        action = torch.tanh(self.layer5(x))
        return action

class Player():
    def __init__(self, x, y, speed_x, speed_y):
        self.body = pygame.Rect(x, y, radius*2, radius*2)
        self.radius = 10
        self.color = None
        self.speed_x = speed_x
        self.speed_y = speed_y
        self.acc_x = 0
        self.acc_y = 0
        self.charge = None
        self.mass = 30

def rotate(speed_x, speed_y, angle):
    return (speed_x*math.cos(angle)-speed_y*math.sin(angle), speed_x*math.sin(angle)+speed_y*math.cos(angle))

def EMField(player_list):
    '''Calculates force through the equations of Coulomb's Law'''
    a = 0
    player_center_list = [player.body.center for player in player_list]
    for player in player_list:
        player_center = player_center_list[a]
        distances = [math.hypot((player_center[0] - player2_center[0]), (player_center[1] - player2_center[1])) for player2_center in player_center_list]
        acc_x = 0
        acc_y = 0
        b = 0
        for player2 in player_list:
            if distances[b] == 0:
                b += 1
                continue
            force = (player.charge*player2.charge)/distances[b]**2
            acc_x += player_center[0] - (player_center[0] - (force/player.mass*(player_center[0]-player_center_list[b][0]))/distances[b])
            acc_y += player_center[1] - (player_center[1] - (force/player.mass*(player_center[1]-player_center_list[b][1]))/distances[b])
            b += 1

        acc_x *= friction
        acc_y *= friction

        player.acc_x = acc_x
        player.acc_y = acc_y
        player.speed_x += acc_x
        player.speed_y += acc_y

        a += 1
    return player_list

def create_charge_data(player_list):
    charge_variables = []
    for player in player_list:
        avg_variable = 0
        count = 0
        sign = 0
        for player2 in player_list:
            x_distance = player.body.centerx - player2.body.centerx
            y_distance = player.body.centery - player2.body.centery
            distance = math.hypot(x_distance, y_distance)
            if distance <= 100:
                distance = distance/100
                avg_variable += distance
                count += 1
                if distance == 0:
                    continue
                elif math.copysign(player2.charge, 1) == player2.charge:
                    sign += 1
                else:
                    sign -= 1
        charge_variables.append(-(math.copysign(avg_variable/count, sign)))
    return charge_variables

def create_end_state(player_list):
    player_avgs = []
    for player in player_list:
        player_distances_avg = sum([math.hypot((player.body.centerx-player2.body.centerx)/screen_width, (player.body.centery - player2.body.centery)/screen_height) for player2 in player_list]) / len(player_list)
        player_avgs.append(player_distances_avg)
    return player_avgs

def Detect_collision(player_list):

    for player in player_list:
        player_body = player.body
        speed_x = player.speed_x
        speed_y = player.speed_y

        '''Player collisions'''
        for player2 in player_list:
            player2_body = player2.body
            player2_speed_x = player2.speed_x
            player2_speed_y = player2.speed_y

            dx = (player_body.centerx-player2_body.centerx)
            dy = (player_body.centery-player2_body.centery)

            distance = math.hypot(dx, dy)

            if distance == 0:
                continue

            if distance <= player.radius + player2.radius:
                angle = -math.atan2((player_body.centery-player2_body.centery), (player_body.centerx-player2_body.centerx))

                init_vel1 = rotate(speed_x, speed_y, angle)
                init_vel2 = rotate(player2_speed_x, player2_speed_y, angle)

                speed_x, speed_y = init_vel2
                player2_speed_x, player2_speed_y = init_vel1

                speed_x, speed_y = rotate(speed_x, speed_y, -angle)
                player2_speed_x, player2_speed_y = rotate(player2_speed_x, player2_speed_y, -angle)

                speed_x *= elasticity
                speed_y *= elasticity

                player2_speed_x *= elasticity
                player2_speed_y *= elasticity

                player2.speed_x = player2_speed_x
                player2.speed_y = player2_speed_y

        '''Making sure Players aren't overlapping'''
        for player2 in player_list:
            player2_body = player2.body
            dx = (player_body.centerx-player2_body.centerx)
            dy = (player_body.centery-player2_body.centery)
            distance = math.hypot(dx, dy)

            if distance == 0:
                continue

            if distance < player.radius + player2.radius:
                tangent = math.atan2(dy,dx)
                overlap = (player.radius + player2.radius - distance)/2
                angle = 0.5 * math.pi + tangent
                player_body.centerx += round(math.sin(angle)*overlap)
                player_body.centery -= round(math.cos(angle)*overlap)
                player2_body.centerx -= round(math.sin(angle)*overlap)
                player2_body.centery += round(math.cos(angle)*overlap)
                player2.body = player2_body


        '''Wall collisions'''
        if player_body.left <= 0:
            player_body.left = 0
            speed_x *= -1

        if player_body.right >= screen_width:
            player_body.right = screen_width
            speed_x *= -1

        if player_body.top <= 0:
            player_body.top = 0
            speed_y *= -1

        if player_body.bottom >= screen_height:
            player_body.bottom = screen_height
            speed_y *= -1


        speed_x *= friction
        speed_y *= friction

        player_body.centerx += round(speed_x)
        player_body.centery += round(speed_y)

        player.body = player_body
        player.speed_x = speed_x
        player.speed_y = speed_y

    return player_list

ChargeNet = chargeNet()

'''Add the path to ChargeNet.tar'''
checkpoint = torch.load("PATH")
ChargeNet.load_state_dict(checkpoint["model"])

beginning_board = [(520, 393, -11, 13), (667, 44, -19, -1), (766, 676, -8, -13), (723, 590, 16, 15), (956, 648, -9, 13), (437, 136, 3, 17), (842, 524, -3, -6), (762, 186, -13, -6), (235, 278, -15, 18), (208, 642, 18, 3), (460, 125, -3, 0), (770, 144, 5, 15), (645, 302, -3, 8), (134, 101, 15, 1), (738, 554, -12, 15), (189, 385, -15, 11), (134, 156, 15, 19), (51, 589, 10, -19), (280, 250, 15, 11), (52, 387, -14, -12)]
'''Should make a circle'''
wanted_pattern = [0.4 for _ in range(20)]

player_list = [Player(x, y, speed_x, speed_y) for (x, y, speed_x, speed_y) in beginning_board]

for index , player in enumerate(player_list):
    player.color = player_colors[index]

action_coefficients = ChargeNet(torch.tensor(wanted_pattern).view(1,20))
action_coefficients = action_coefficients[0].tolist()

bg_color = pygame.Color('grey12')

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
    
    charge_variables = create_charge_data(player_list)
    charge_list = [sum([(a*100)*(x**n) for n,a in enumerate(action_coefficients)]) for x in charge_variables]

    for index , player in enumerate(player_list):
        player.charge = charge_list[index]
    
    player_list = EMField(player_list)
    player_list = Detect_collision(player_list)
    
    screen.fill(bg_color)
    for player in player_list:
        pygame.draw.ellipse(screen, pygame.Color(player.color), player.body)

    pygame.display.flip()
    clock.tick(60)
                
