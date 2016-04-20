#! /usr/bin/env python3

# -*- coding: utf-8 -*-


import pygame, sys
from pygame.locals import *
WIDTH = 800
HEIGHT = 600
n_big_stars = 80
n_small_stars = 120
heli_y = HEIGHT/2
big_stars_speed = 0.4
small_stars_speed = 0.7
flag = True
up = False
down = False
heli_y_ = heli_y

pygame.init()

DISPLAYSURF = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('RETURN TO SAIGON')
STARSURF = pygame.image.load_basic('star.bmp')
HELI_SURF = pygame.image.load_basic('copter2.bmp')

import random
r = random.Random()

coords = []
coords_slow = []

for i in range(n_big_stars):
    coords.append((r.randint(20, WIDTH - 20),r.randint(20, HEIGHT - 20)))
for i in range(n_big_stars):
    DISPLAYSURF.blit(STARSURF, coords[i])

for i in range(n_small_stars):
    coords_slow.append((r.randint(20, WIDTH - 20),r.randint(20, HEIGHT - 20)))
for i in range(n_small_stars):
    DISPLAYSURF.fill(color.Color('Yellow'),pygame.rect.Rect(coords_slow[i][0],coords_slow[i][1],1,1))

DISPLAYSURF.blit(HELI_SURF, (100, heli_y),pygame.rect.Rect(0,0,32,24))

heli_v_y_ = 0.0
fire = False
projectiles = []

def fillBlack():
    pass
# pygame.Surface.fill
while True:
    # main game loop
    if up:
        heli_v_y_ -= 0.015
    if down:
        heli_v_y_ += 0.015
    if fire:
        projectiles.append((135,heli_y+10))
        fire = not fire

    for i in range(n_big_stars):
        DISPLAYSURF.fill(color.Color('Black'),pygame.rect.Rect(int(coords[i][0]),coords[i][1],8,8))
    for i in range(n_small_stars):
        DISPLAYSURF.fill(color.Color('Black'),pygame.rect.Rect(int(coords_slow[i][0]),coords_slow[i][1],1,1))
    DISPLAYSURF.fill(color.Color('Black'),pygame.rect.Rect(100,heli_y,32,24))

    for proj in projectiles:
        DISPLAYSURF.fill(color.Color('Black'), pygame.rect.Rect(proj[0],proj[1],4,1))

    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        if event.type == KEYDOWN:
            if event.key == K_s:
                down = True
                up = False
            if event.key == K_w:
                up = True
                down = False
            if event.key == K_SPACE:
                fire = True
        if event.type == KEYUP:
            if event.key == K_s:
                down = False
            if event.key == K_w:
                up = False

    for i in range(n_big_stars):
        coords[i] = divmod(coords[i][0]-big_stars_speed,WIDTH)[1], coords[i][1]
        DISPLAYSURF.blit(STARSURF, (int(coords[i][0]),coords[i][1]))
    for i in range(n_small_stars):
        coords_slow[i] = divmod(coords_slow[i][0]-small_stars_speed, WIDTH)[1], coords_slow[i][1]
        DISPLAYSURF.fill(color.Color('Yellow'),pygame.rect.Rect(int(coords_slow[i][0]),coords_slow[i][1],1,1))

    projectiles = [(p[0] + 3, p[1]) for p in projectiles if p[0] < WIDTH]
    for proj in projectiles:
        DISPLAYSURF.fill(color.Color('White'), pygame.rect.Rect(proj[0],proj[1], 4, 1))


    heli_y_ += heli_v_y_
    heli_y = int(heli_y_)
    heli_v_y_ *= 0.96
    if flag:
        x = 32
        flag = not flag
    else:
        x = 0
        flag = not flag
    DISPLAYSURF.blit(HELI_SURF,(100,heli_y),pygame.rect.Rect(x,0,32,24))
    pygame.display.update()
