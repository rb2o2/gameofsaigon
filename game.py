#! /usr/bin/env python3

# -*- coding: utf-8 -*-
import pygame, sys
from pygame.locals import *

WIDTH = 800
HEIGHT = 600
n_big_stars = 40
n_small_stars = 120
heli_y = HEIGHT/2
big_stars_speed = 0.4
small_stars_speed = 0.7
GROUND_Y = 550

flag = True
up = False
down = False
heli_y_ = heli_y

pygame.init()

DISPLAYSURF = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('RETURN TO SAIGON')
STARSURF = pygame.image.load_basic('star.bmp')
HELISURF = pygame.image.load_basic('copter.bmp')
MIGSURF = pygame.image.load_basic('Mig15.bmp')
HUTSURF = pygame.image.load_basic('hut.bmp')
PALMSURF = pygame.image.load_basic('palmTree.bmp')
BOMBSURF = pygame.image.load_basic('bomb.bmp')
FLAMESURF = pygame.image.load_basic('flame.bmp')

import random
r = random.Random()

coords = []
coords_slow = []

for i in range(n_big_stars):
    coords.append((r.randint(20, WIDTH - 20),r.randint(20, GROUND_Y - 20)))
for i in range(n_big_stars):
    DISPLAYSURF.blit(STARSURF, coords[i])

for i in range(n_small_stars):
    coords_slow.append((r.randint(20, WIDTH - 20),r.randint(20, GROUND_Y - 20)))
for i in range(n_small_stars):
    DISPLAYSURF.fill(color.Color('Yellow'),pygame.rect.Rect(coords_slow[i][0],coords_slow[i][1],1,1))

DISPLAYSURF.blit(HELISURF, (100, heli_y), pygame.rect.Rect(0, 0, 32, 24))

heli_v_y_ = 0.0
fire = False
bomb = False
projectiles = []
enemies = []
frame_counter = 0
frame_counter_MAX = 800
hutten = []
trees = []
bombs = []
flame = []
bomb_init_speed = 0.0035
flame_frame_counter_max = 25
flame_counter = 0
shl = 0


for i in range(0,WIDTH -32, 64):
    choice = r.choice(["hut","tree"])
    if choice == "hut":
        hutten.append((i,GROUND_Y - 32))
    elif choice == "tree":
        trees.append((i, GROUND_Y - 64))

def fillBlack():
    for i in range(n_big_stars):
        DISPLAYSURF.fill(color.Color('Black'), pygame.rect.Rect(int(coords[i][0]), coords[i][1], 8, 8))
    for i in range(n_small_stars):
        DISPLAYSURF.fill(color.Color('Black'), pygame.rect.Rect(int(coords_slow[i][0]), coords_slow[i][1], 1, 1))
    DISPLAYSURF.fill(color.Color('Black'), pygame.rect.Rect(100, heli_y, 32, 24))
    for proj in projectiles:
        DISPLAYSURF.fill(color.Color('Black'), pygame.rect.Rect(proj[0], proj[1], 20, 1))
    for enemy in enemies:
        DISPLAYSURF.fill(color.Color('Black'), pygame.rect.Rect(enemy[0],enemy[1], 32, 32))
    for hut in hutten:
        DISPLAYSURF.fill(color.Color('Black'), pygame.rect.Rect(hut[0], hut[1], 32, 32))
    for tree in trees:
        DISPLAYSURF.fill(color.Color('Black'), pygame.rect.Rect(tree[0], tree[1], 32, 64))
    for b in bombs:
        DISPLAYSURF.fill(color.Color('Black'), pygame.rect.Rect(int(b[0]), int(b[1]), 16, 16))
    for fl in flame:
        DISPLAYSURF.fill(color.Color('Black'), pygame.rect.Rect(int(fl[0]), int(fl[1]), 32, 32))

def launch_enemy():
    enemy_y = r.randint(20, GROUND_Y - 64 - 20)
    enemies.append((WIDTH, enemy_y))

def drop_bomb():
    bombs.append((100, heli_y + 24, bomb_init_speed))

# pygame.Surface.fill
while True:
    flame_counter += 1
    frame_counter += 1
    if frame_counter == frame_counter_MAX:
        launch_enemy()
        frame_counter = 0

    if flame_counter == flame_frame_counter_max:
        flame_counter = 0
        shl = 32 - shl
    # main game loop
    if up:
        heli_v_y_ -= 0.015
    if down:
        heli_v_y_ += 0.015
    if fire:
        projectiles.append((135,heli_y+10))
        fire = not fire
    if bomb:
        drop_bomb()
        bomb = not bomb

    fillBlack()

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
            if event.key == K_m:
                bomb = True
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

    projectiles = [(p[0] + 3, p[1]) for p in projectiles if p[0] < WIDTH + 20]
    for proj in projectiles:
        DISPLAYSURF.fill(color.Color('White'), pygame.rect.Rect(proj[0],proj[1], 20, 1))


    flame_to_append = [(92.0, GROUND_Y - 32) for b in bombs if b[1] > (GROUND_Y - 16)]
    flame = flame + flame_to_append

    bombs = [(b[0], b[1]+b[2],min(b[2]+bomb_init_speed,3)) for b in bombs if b[1] < (GROUND_Y - 16)]
    for b in bombs:
        DISPLAYSURF.blit(BOMBSURF, (int(b[0]),int(b[1])))

    flame = [(divmod(f[0] - 0.25, WIDTH)[1], f[1]) for f in flame]



    hutten = [(divmod(h[0] - 0.25, WIDTH)[1], h[1]) for h in hutten]
    trees = [(divmod(t[0] - 0.25, WIDTH)[1], t[1]) for t in trees]
    for h in hutten:
        DISPLAYSURF.blit(HUTSURF, (int(h[0]), int(h[1])))
    for t in trees:
        DISPLAYSURF.blit(PALMSURF, (int(t[0]), int(t[1])))
    for f in flame:
        DISPLAYSURF.blit(FLAMESURF, (int(f[0]), int(f[1])), pygame.rect.Rect(shl,0,32,32))

    enemies = [(e[0] - 0.3,e[1]) for e in enemies if e[0] > -32]
    for enemy in enemies:
        DISPLAYSURF.blit(MIGSURF, (int(enemy[0]),int(enemy[1])))

    heli_y_ += heli_v_y_
    heli_y = int(heli_y_)
    heli_v_y_ *= 0.96
    if flag:
        x = 32
        flag = not flag
    else:
        x = 0
        flag = not flag
    DISPLAYSURF.blit(HELISURF, (100, heli_y), pygame.rect.Rect(x, 0, 32, 24))
    pygame.display.update()
