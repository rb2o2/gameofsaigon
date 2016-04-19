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
for i in range(80):
    coords.append((r.randint(20, WIDTH - 20),r.randint(20, HEIGHT - 20)))
for i in range(80):
    DISPLAYSURF.blit(STARSURF, coords[i])
HELI_SURF = pygame.image.load_basic('copter2.bmp')
DISPLAYSURF.set_clip(pygame.rect.Rect(100,HEIGHT/2,32, 24))
DISPLAYSURF.blit(HELI_SURF, (100, HEIGHT/2))
# pygame.Surface.blit
flag = True
while True:
# main game loop
    DISPLAYSURF.set_clip(None)
    for i in range(80):
        DISPLAYSURF.fill(color.Color('Black'),pygame.rect.Rect(coords[i][0],coords[i][1],8,8))
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
    for i in range(80):
        coords[i] = divmod(coords[i][0]-1,WIDTH)[1], coords[i][1]
        DISPLAYSURF.blit(STARSURF, coords[i])
    DISPLAYSURF.set_clip(pygame.rect.Rect(100,HEIGHT/2,32,24))
    if flag:
        x = 32
        flag = not flag
    else:
        x = 0
        flag = not flag
    DISPLAYSURF.blit(HELI_SURF,(100,HEIGHT/2),pygame.rect.Rect(x,0,32,24))
    pygame.display.update()
