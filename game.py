#! /usr/bin/env python3

# -*- coding: utf-8 -*-


import pygame, sys
from pygame.locals import *
WIDTH = 800
HEIGHT = 600

pygame.init()
DISPLAYSURF = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('RETURN TO SAIGON')
STARSURF = pygame.image.load_basic('star.bmp')
import random
r = random.Random()
coords = []
coords_slow = []
for i in range(80):
    coords.append((r.randint(20, WIDTH - 20),r.randint(20, HEIGHT - 20)))
for i in range(120):
    coords_slow.append((r.randint(20, WIDTH - 20),r.randint(20, HEIGHT - 20)))
for i in range(80):
    DISPLAYSURF.blit(STARSURF, coords[i])
for i in range(120):
    DISPLAYSURF.fill(color.Color('Yellow'),pygame.rect.Rect(coords_slow[i][0],coords_slow[i][1],1,1))
HELI_SURF = pygame.image.load_basic('copter2.bmp')
heli_y = HEIGHT/2
heli_v_y_ = 0.0
DISPLAYSURF.blit(HELI_SURF, (100, heli_y),pygame.rect.Rect(0,0,32,24))
# pygame.Surface.fill
flag = True
up = False
down = False
heli_y_ = heli_y
while True:
    # main game loop
    if up:
        heli_v_y_ -= 0.015
    if down:
        heli_v_y_ += 0.015
    # heli_v_y = int(heli_v_y_)
    for i in range(80):
        DISPLAYSURF.fill(color.Color('Black'),pygame.rect.Rect(coords[i][0],coords[i][1],8,8))
    for i in range(120):
        DISPLAYSURF.fill(color.Color('Black'),pygame.rect.Rect(int(coords_slow[i][0]),coords_slow[i][1],1,1))
    DISPLAYSURF.fill(color.Color('Black'),pygame.rect.Rect(100,heli_y,32,24))
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
        if event.type == KEYUP:
            if event.key == K_s:
                down = False
            if event.key == K_w:
                up = False
    for i in range(80):
        coords[i] = divmod(coords[i][0]-1,WIDTH)[1], coords[i][1]
        DISPLAYSURF.blit(STARSURF, coords[i])
    for i in range(120):
        coords_slow[i] = divmod(coords_slow[i][0]-0.4, WIDTH)[1], coords_slow[i][1]
        DISPLAYSURF.fill(color.Color('Yellow'),pygame.rect.Rect(int(coords_slow[i][0]),coords_slow[i][1],1,1))
    heli_y_ += heli_v_y_
    heli_y = int(heli_y_)
    heli_v_y_ *= 0.97
    if flag:
        x = 32
        flag = not flag
    else:
        x = 0
        flag = not flag
    DISPLAYSURF.blit(HELI_SURF,(100,heli_y),pygame.rect.Rect(x,0,32,24))
    pygame.display.update()
