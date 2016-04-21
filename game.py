#! /usr/bin/env python3

# -*- coding: utf-8 -*-
import math
import pygame, sys
import random
from pygame.locals import *


class Explosion(object):
    def __init__(self, x, y, n=20, init_v=0.9, alpha=math.pi, v_x=0.3, max_frames=400.0, r=random.Random()):
        self.particles = []
        self.max_frames = max_frames
        self.frame = 0
        for i in range(n):
            angle = r.uniform(-alpha, alpha)
            dev = r.gauss(1.0, 0.2)
            self.particles.append((x, y, math.sin(angle) * init_v * dev + v_x, -math.cos(angle) * init_v * dev))

    def fill_black_surf(self, surf, particle_size):
        for part in self.particles:
            surf.fill(color.Color('Black'), pygame.rect.Rect(int(part[0]), int(part[1]), particle_size, particle_size))

    def redraw_on_surf(self, surf, particle_size):
        def blend(x):
            if 0.0 <= x < self.max_frames/3:
                return pygame.Color(255, 255, int(255 - 255 * (x/self.max_frames * 3)), 0)
            if float(self.max_frames) / 3 <= x < 2. * self.max_frames / 3:
                return pygame.Color(255, int(2 * 255 - 255.0 * (x / self.max_frames * 3)), 0, 0)
            if 2*self.max_frames/3 <= x <= self.max_frames:
                return pygame.Color(3 * 255 - int(3.0 * x / self.max_frames * 255), 0, 0, 0)

        self.frame += 1.0
        self.particles = [
            (p[0] + p[2],
             p[1] + p[3],
             p[2] * 0.99,
             p[3] * 0.99 + 0.0001)
            for p in self.particles
            if self.frame < self.max_frames
            ]
        for p in self.particles:
            surf.fill(blend(self.frame), pygame.rect.Rect(int(p[0]), int(p[1]), particle_size, particle_size))


class Game(object):
    def __init__(self):
        self.WIDTH = 800
        self.HEIGHT = 600
        self.n_big_stars = 40
        self.n_small_stars = 100
        self.heli_y = self.HEIGHT / 2
        self.big_stars_speed = 0.4
        self.small_stars_speed = 0.7
        self.GROUND_Y = 550
        self.TRACER_LENGTH = 20
        self.particle_size = 2
        self.BOMBS_MAX = 8
        self.r = random.Random()

        self.heli_frame_flag = True
        self.up_flag = False
        self.down_flag = False
        self.heli_y_ = self.heli_y
        self.fire_flag = False
        self.bomb_flag = False

        self.sprites = {}
        self.sprites['projectiles'] = []
        self.sprites['enemies'] = []
        self.sprites['hutten'] = []
        self.sprites['trees'] = []
        self.sprites['bombs'] = []
        self.sprites['flame'] = []
        self.sprites['explosions'] = []
        self.sprites['star_coords'] = []
        self.sprites['slow_stars_coords'] = []

        self.heli_v_y_ = 0.0
        self.enemy_frame_counter = 0
        self.enemy_frame_counter_MAX = 1000
        self.bomb_init_speed = 0.0035
        self.flame_counter_MAX = 25
        self.flame_counter = 0
        self.shl = 0
        self.ammo = {'bombs_left': self.BOMBS_MAX}

        pygame.init()
        self.DISPLAYSURF = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption('RETURN TO SAIGON')

        self.STARSURF = pygame.image.load_basic('star.bmp')
        self.HELISURF = pygame.image.load_basic('copter.bmp')
        self.MIGSURF = pygame.image.load_basic('Mig15.bmp')
        self.HUTSURF = pygame.image.load_basic('hut.bmp')
        self.PALMSURF = pygame.image.load_basic('palmTree.bmp')
        self.BOMBSURF = pygame.image.load_basic('bomb.bmp')
        self.FLAMESURF = pygame.image.load_basic('flame.bmp')
        for i in range(self.n_big_stars):
            self.sprites['star_coords'].append(
                (self.r.randint(20, self.WIDTH - 20),
                 self.r.randint(20, self.GROUND_Y - 20))
            )
        for i in range(self.n_small_stars):
            self.sprites['slow_stars_coords'].append(
                (self.r.randint(20, self.WIDTH - 20),
                 self.r.randint(20, self.GROUND_Y - 20))
            )
        for i in range(0, self.WIDTH - 32, 48):
            choice = self.r.choice(["hut", "tree"])
            if choice == "hut":
                self.sprites['hutten'].append((i, self.GROUND_Y - 32))
            elif choice == "tree":
                self.sprites['trees'].append((i, self.GROUND_Y - 64))

    def fill_black(self):
        for i in range(self.n_big_stars):
            self.DISPLAYSURF.fill(
                color.Color('Black'),
                pygame.rect.Rect(int(self.sprites['star_coords'][i][0]),
                                 self.sprites['star_coords'][i][1],
                                 8,
                                 8)
            )
        for i in range(self.n_small_stars):
            self.DISPLAYSURF.fill(
                color.Color('Black'),
                pygame.rect.Rect(int(self.sprites['slow_stars_coords'][i][0]),
                                 self.sprites['slow_stars_coords'][i][1],
                                 1,
                                 1)
            )
        self.DISPLAYSURF.fill(
            color.Color('Black'),
            pygame.rect.Rect(100,
                             self.heli_y,
                             32,
                             24)
        )
        for proj in self.sprites['projectiles']:
            self.DISPLAYSURF.fill(
                color.Color('Black'),
                pygame.rect.Rect(
                    proj[0],
                    proj[1],
                    self.TRACER_LENGTH,
                    1))
        for enemy in self.sprites['enemies']:
            self.DISPLAYSURF.fill(
                color.Color('Black'),
                pygame.rect.Rect(
                    enemy[0],
                    enemy[1],
                    32,
                    32)
            )
        for hut in self.sprites['hutten']:
            self.DISPLAYSURF.fill(
                color.Color('Black'),
                pygame.rect.Rect(
                    hut[0],
                    hut[1],
                    32,
                    32)
            )
        for tree in self.sprites['trees']:
            self.DISPLAYSURF.fill(
                color.Color('Black'),
                pygame.rect.Rect(
                    tree[0],
                    tree[1],
                    32,
                    64)
            )
        for b in self.sprites['bombs']:
            self.DISPLAYSURF.fill(
                color.Color('Black'),
                pygame.rect.Rect(
                    int(b[0]),
                    int(b[1]),
                    16,
                    16)
            )
        for fl in self.sprites['flame']:
            self.DISPLAYSURF.fill(
                color.Color('Black'),
                pygame.rect.Rect(
                    int(fl[0]),
                    int(fl[1]),
                    32,
                    32)
            )

    def init_scene(self):
        for i in range(self.BOMBS_MAX):
            self.DISPLAYSURF.blit(self.BOMBSURF, (1 + i * 17, 1))
        for i in range(self.n_big_stars):
            self.DISPLAYSURF.blit(self.STARSURF, self.sprites['star_coords'][i])
        for i in range(self.n_small_stars):
            self.DISPLAYSURF.fill(
                color.Color('Yellow'),
                pygame.rect.Rect(
                    self.sprites['slow_stars_coords'][i][0],
                    self.sprites['slow_stars_coords'][i][1],
                    1,
                    1)
            )
        self.DISPLAYSURF.blit(
            self.HELISURF,
            (100, self.heli_y),
            pygame.rect.Rect(0, 0, 32, 24))

    def redraw_sprites(self):
        for i in range(self.n_big_stars):
            self.sprites['star_coords'][i] = (
                divmod(
                    self.sprites['star_coords'][i][0] - self.big_stars_speed,
                    self.WIDTH
                )[1],
                self.sprites['star_coords'][i][1]
            )
            self.DISPLAYSURF.blit(
                self.STARSURF,
                (int(self.sprites['star_coords'][i][0]),
                 self.sprites['star_coords'][i][1])
            )
        for i in range(self.n_small_stars):
            self.sprites['slow_stars_coords'][i] = (
                divmod(
                    self.sprites['slow_stars_coords'][i][0] - self.small_stars_speed,
                    self.WIDTH
                )[1],
                self.sprites['slow_stars_coords'][i][1]
            )
            self.DISPLAYSURF.fill(
                color.Color('Yellow'),
                pygame.rect.Rect(
                    int(self.sprites['slow_stars_coords'][i][0]),
                    self.sprites['slow_stars_coords'][i][1],
                    1,
                    1)
            )

        self.sprites['projectiles'] = [
            (p[0] + 3, p[1]) for p in self.sprites['projectiles']
            if p[0] < self.WIDTH + 20
            ]
        for proj in self.sprites['projectiles']:
            self.DISPLAYSURF.fill(
                color.Color('White'),
                pygame.rect.Rect(
                    proj[0],
                    proj[1],
                    20,
                    1)
            )

        flame_to_append = [
            (92.0, self.GROUND_Y - 32) for b in self.sprites['bombs']
            if b[1] > (self.GROUND_Y - 16)
            ]
        self.sprites['flame'] = self.sprites['flame'] + flame_to_append

        self.sprites['explosions'] = [
            ex for ex in self.sprites['explosions']
            if ex.frame < ex.max_frames
            ]

        bomb_explosion = [
            Explosion(92, self.GROUND_Y, n=30, init_v=0.6, alpha=math.pi / 3)
            for b in self.sprites['bombs']
            if b[1] > (self.GROUND_Y - 16)
            ]
        self.sprites['explosions'] = self.sprites['explosions'] + bomb_explosion

        self.sprites['bombs'] = [
            (b[0], b[1] + b[2], min(b[2] + self.bomb_init_speed, 3))
            for b in self.sprites['bombs']
            if b[1] < (self.GROUND_Y - 16)
            ]
        for b in self.sprites['bombs']:
            self.DISPLAYSURF.blit(self.BOMBSURF, (int(b[0]), int(b[1])))

        for x in self.sprites['explosions']:
            x.redraw_on_surf(self.DISPLAYSURF, self.particle_size)

        self.sprites['flame'] = [
            (divmod(f[0] - 0.25 + 32, self.WIDTH + 32)[1] - 32, f[1])
            for f in self.sprites['flame']
            ]

        self.sprites['hutten'] = [
            (divmod(h[0] - 0.25 + 32, self.WIDTH + 32)[1] - 32, h[1])
            for h in self.sprites['hutten']
            ]
        self.sprites['trees'] = [
            (divmod(t[0] - 0.25 + 32, self.WIDTH + 32)[1] - 32, t[1])
            for t in self.sprites['trees']
            ]

        for h in self.sprites['hutten']:
            self.DISPLAYSURF.blit(self.HUTSURF, (int(h[0]), int(h[1])))

        for t in self.sprites['trees']:
            self.DISPLAYSURF.blit(self.PALMSURF, (int(t[0]), int(t[1])))

        for f in self.sprites['flame']:
            self.DISPLAYSURF.blit(
                self.FLAMESURF,
                (int(f[0]), int(f[1])),
                pygame.rect.Rect(self.shl, 0, 32, 32)
            )

        self.sprites['enemies'] = [
            (e[0] - 0.3, e[1])
            for e in self.sprites['enemies']
            if e[0] > -32
            ]
        for enemy in self.sprites['enemies']:
            self.DISPLAYSURF.blit(
                self.MIGSURF,
                (int(enemy[0]), int(enemy[1]))
            )

        enemies_hit = []

        for p in self.sprites['projectiles']:
            for mig in self.sprites['enemies']:
                if mig[1] + 4 < p[1] < mig[1] - 4 + 32 and mig[0] + 4 < p[0] + 20 < mig[0] + 24:
                    enemies_hit.append((p, mig))
        for p, mig in enemies_hit:
            self.DISPLAYSURF.fill(
                color.Color('Black'),
                pygame.rect.Rect(
                    p[0],
                    p[1],
                    self.TRACER_LENGTH,
                    1)
            )
            self.DISPLAYSURF.fill(
                color.Color('Black'),
                pygame.rect.Rect(
                    mig[0],
                    mig[1],
                    32,
                    32)
            )

            self.sprites['enemies'].remove(mig)
            self.sprites['projectiles'].remove(p)
            self.sprites['explosions'].append(Explosion(mig[0] + 4, mig[1] + 16, init_v=0.35, n=60, max_frames=300))
            self.sprites['explosions'].append(Explosion(mig[0] + 4, mig[1] + 16, init_v=0.17, n=30, max_frames=180.0))

        self.heli_y_ += self.heli_v_y_
        self.heli_y = int(self.heli_y_)
        self.heli_v_y_ *= 0.96
        if self.heli_frame_flag:
            x = 32
            self.heli_frame_flag = not self.heli_frame_flag
        else:
            x = 0
            self.heli_frame_flag = not self.heli_frame_flag
        self.DISPLAYSURF.blit(
            self.HELISURF,
            (100, self.heli_y),
            pygame.rect.Rect(x, 0, 32, 24)
        )

    def launch_enemy(self):
        enemy_y = self.r.randint(20, self.GROUND_Y - 64 - 20)
        self.sprites['enemies'].append((self.WIDTH, enemy_y))

    def drop_bomb(self):
        self.sprites['bombs'].append((100, self.heli_y + 24, self.bomb_init_speed))
        self.ammo['bombs_left'] -= 1
        self.DISPLAYSURF.fill(
            color.Color('Black'),
            pygame.rect.Rect(
                1 + 17 * self.ammo['bombs_left'],
                1,
                16,
                16)
        )

    def process_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_s:
                    self.down_flag = True
                    self.up_flag = False
                if event.key == K_w:
                    self.up_flag = True
                    self.down_flag = False
                if event.key == K_SPACE:
                    self.fire_flag = True
                if event.key == K_m and self.ammo.get('bombs_left') > 0:
                    self.bomb_flag = True
            if event.type == KEYUP:
                if event.key == K_s:
                    self.down_flag = False
                if event.key == K_w:
                    self.up_flag = False

    def loop(self):
        self.init_scene()
        while True:
            self.flame_counter += 1
            self.enemy_frame_counter += 1
            if self.enemy_frame_counter == self.enemy_frame_counter_MAX:
                self.launch_enemy()
                self.enemy_frame_counter = 0
            if self.flame_counter == self.flame_counter_MAX:
                self.flame_counter = 0
                self.shl = 32 - self.shl
            if self.up_flag:
                self.heli_v_y_ -= 0.015
            if self.down_flag:
                self.heli_v_y_ += 0.015
            if self.fire_flag:
                self.sprites['projectiles'].append((135, self.heli_y + 10))
                self.fire_flag = not self.fire_flag
            if self.bomb_flag:
                self.drop_bomb()
                self.bomb_flag = not self.bomb_flag

            self.fill_black()
            for ex in self.sprites['explosions']:
                ex.fill_black_surf(self.DISPLAYSURF, self.particle_size)

            self.process_events()

            self.redraw_sprites()

            pygame.display.update()


game = Game()
game.loop()
