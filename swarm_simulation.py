import pygame
import math, sys
from random import randint

pygame.init()
clock = pygame.time.Clock()

screen_width = 1000
screen_height = 700
friction = 0.9999
elasticity = 0.6
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Swarm")

class Player():
    def __init__(self, x, y, mass, charge, radius):
        self.body = pygame.Rect(x, y, radius*2, radius*2)
        self.radius = radius
        self.speed_x = 15
        self.speed_y = -15
        self.acc_x = 0
        self.acc_y = 0
        self.charge = charge
        self.mass = mass


def rotate(speed_x, speed_y, angle):
    return (speed_x*math.cos(angle)-speed_y*math.sin(angle), speed_x*math.sin(angle)+speed_y*math.cos(angle))

def EMField(player_list):
    '''Calculates force through the equations of Coulomb's Law'''
    a = 0
    player_center_list = [tuple([player.body.centerx, player.body.centery]) for player in player_list]
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

                mass1 = player.mass
                mass2 = player2.mass

                init_vel1 = rotate(speed_x, speed_y, angle)
                init_vel2 = rotate(player2_speed_x, player2_speed_y, angle)

                speed_x, speed_y = ((init_vel1[0]*(mass1-mass2)/(mass1+mass2)) + (init_vel2[0]*2*mass2/(mass1 + mass2))), init_vel1[1]
                player2_speed_x, player2_speed_y = ((init_vel2[0]*(mass1-mass2)/(mass1+mass2)) + (init_vel1[0]*2*mass2/(mass1 + mass2))), init_vel2[1]

                speed_x, speed_y = rotate(speed_x, speed_y, -angle)

                speed_x *= elasticity
                speed_y *= elasticity

                player2_speed_x, player2_speed_y = rotate(player2_speed_x, player2_speed_y, -angle)

                player2_speed_x *= elasticity
                player2_speed_y *= elasticity

                player2.body = player2_body
                player2.speed_x = player2_speed_x
                player2.speed_y = player2_speed_y

        '''Making sure Players aren't overlapping'''
        for player2 in player_list:
            player2_body = player2.body
            player2_speed_x = player2.speed_x
            player2_speed_y = player2.speed_y

            dx = (player_body.centerx-player2_body.centerx)
            dy = (player_body.centery-player2_body.centery)

            distance = math.hypot(dx, dy)

            if distance == 0:
                continue

            if distance < player.radius + player2.radius:
                tangent = math.atan2(dy,dx)
                overlap = (player.radius + player2.radius - distance)/2
                angle = 0.5 * math.pi + tangent
                player_body.centerx += math.sin(angle)*overlap
                player_body.centery -= math.cos(angle)*overlap
                player2_body.centerx -= math.sin(angle)*overlap
                player2_body.centery += math.cos(angle)*overlap
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

        player.speed_x = speed_x
        player.speed_y = speed_y

    return player_list

def rand_x():
    return randint(20,screen_width-20)
def rand_y():
    return randint(20,screen_height-20)


player_list = []
charge_list = [50, 50, 50, 50, 50, 50, -50, 50, 50, 50, 50, 50, 50, 50, 50]

for charge in charge_list:
    player_list.append(Player(rand_x(), rand_y(), 100, charge, 10))

bg_color = pygame.Color('grey12')
p_color = (200,150,200)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    player_list = EMField(player_list)
    player_list = Detect_collision(player_list)
    screen.fill(bg_color)
    for player in player_list:
        pygame.draw.ellipse(screen, p_color, player.body)

    pygame.display.flip()
    clock.tick(60)
                
