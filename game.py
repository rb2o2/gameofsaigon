#! /usr/bin/env python3

# -*- coding: utf-8 -*-
import math
import pygame, sys
from pygame.locals import *

WIDTH = 800
HEIGHT = 600
n_big_stars = 40
n_small_stars = 100
heli_y = HEIGHT/2
big_stars_speed = 0.4
small_stars_speed = 0.7
GROUND_Y = 550
TRACER_LENGTH = 20

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
explosions = []
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

class explosion(object):
    def __init__(self, x, y, n=20, init_v=0.9, alpha=math.pi):
        self.particles = []
        self.max_frames = 400.0
        for i in range(n):
            angle = r.uniform(-alpha, alpha)
            dev = r.gauss(1.0,0.2)
            self.particles.append((x, y, math.cos(angle) * init_v * dev, math.sin(angle) * init_v * dev, 0.0))

    def fillBlackSurf(self,surf):
        for part in self.particles:
            surf.fill(color.Color('Black'),pygame.rect.Rect(int(part[0]),int(part[1]),1,1))

    def recalcOnSurface(self,surf):
        def blend(x):

            if 0.0 <= x < self.max_frames/3:
                return pygame.Color(255, 255, int(255 - 255 * (x/self.max_frames * 3)), 0)
            if self.max_frames/3 <= x < 2*self.max_frames/3:
                return pygame.Color(255, int(2*255 - 255*(x/self.max_frames * 3)),0,0)
            if 2*self.max_frames/3 <= x <= self.max_frames:
                return pygame.Color(3 * 255 - int(3.0 * x / self.max_frames * 255), 0, 0, 0)
        self.particles = [(p[0]+p[2],p[1]+p[3],p[2]*0.99,p[3]*0.99+0.0001,p[4]+1.0) for p in self.particles if p[4] < self.max_frames]
        for p in self.particles:
            surf.fill(blend(p[4]),pygame.rect.Rect(int(p[0]),int(p[1]),1,1))



import math


explosions.append(explosion(float(WIDTH/2), float(HEIGHT/2), n=120, init_v=0.32))
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
    for ex in explosions:
        ex.fillBlackSurf(DISPLAYSURF)

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

    for x in explosions:
        x.recalcOnSurface(DISPLAYSURF)

    flame = [(divmod(f[0] - 0.25 + 32, WIDTH + 32)[1] - 32, f[1]) for f in flame]



    hutten = [(divmod(h[0] - 0.25 + 32, WIDTH + 32)[1] - 32, h[1]) for h in hutten]
    trees = [(divmod(t[0] - 0.25 + 32, WIDTH + 32)[1] - 32, t[1]) for t in trees]
    for h in hutten:
        DISPLAYSURF.blit(HUTSURF, (int(h[0]), int(h[1])))
    for t in trees:
        DISPLAYSURF.blit(PALMSURF, (int(t[0]), int(t[1])))
    for f in flame:
        DISPLAYSURF.blit(FLAMESURF, (int(f[0]), int(f[1])), pygame.rect.Rect(shl,0,32,32))

    enemies = [(e[0] - 0.3,e[1]) for e in enemies if e[0] > -32]
    for enemy in enemies:
        DISPLAYSURF.blit(MIGSURF, (int(enemy[0]),int(enemy[1])))

    enemies_hit = []
    for p in projectiles:
        for mig in enemies:
            if mig[1] + 4 < p[1] < mig[1] - 4 + 32 and mig[0] + 4 < p[0] + 20 < mig[0] + 24:
                enemies_hit.append((p, mig))
    for p, mig in enemies_hit:
        fillBlack()
        enemies.remove(mig)
        projectiles.remove(p)
        explosions.append(explosion(mig[0] + 4, mig[1] + 16, init_v=0.5, n=200))

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
