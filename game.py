#! /usr/bin/env python3

# -*- coding: utf-8 -*-
import math
import pygame, sys
import random
import json
from pygame.locals import *
from pygame.transform import rotate

global counter


class anim_seq(object):
    pass


class GameObject(object):
    def __init__(self, config):
        self.frames = config['frame_seq']
        self.x = config['x']
        self.y = config['y']
        self.v_x = config['v_x']
        self.v_y = config['v_y']


class MissionControl(object):
    def __init__(self):
        self.spriteToCode = {
            "SAM": 'sams',
            "MiG": 'enemies'
        }
        self.currentMission = 1
        f = open('mission.json', 'rt')
        enc = json.JSONDecoder()
        self.missions = enc.decode(''.join(f.readlines()))
        self.current = {}
        for a in self.missionGoal().keys():
            self.current[a] = 0
        f.close()

    def missionGoal(self):
        i = self.currentMission - 1
        goal = self.missions[i]
        result = {}
        for key in goal.keys():
            result[self.spriteToCode[key]] = goal[key]
        return result

    def down(self, spriteType):
        self.current[spriteType] = self.current[spriteType] + 1


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
        self.MC = MissionControl()
        # random refactoring
        self.endgame_counter = 0
        self.endgame_lost = False
        self.endgame_won = False
        self.WIDTH = 800
        self.HEIGHT = 600
        self.n_big_stars = 40
        self.n_small_stars = 100
        self.heli_y = self.HEIGHT / 2
        self.big_stars_speed = 0.4
        self.small_stars_speed = 0.7
        self.GROUND_SPEED = 0.25
        self.GROUND_Y = 550
        self.TRACER_LENGTH = 20
        self.particle_size = 2
        self.BOMBS_MAX = 8
        self.r = random.Random()
        self.game_over_counter = 0
        self.mission_complete_counter = 0
        self.mission_complete_flag = False

        self.heli_frame_flag = True
        self.up_flag = False
        self.down_flag = False
        self.tangage_flag_up = False
        self.tangage_flag_down = False
        self.tangage_angle = 0
        self.tangage_speed = 0
        self.heli_y_ = self.heli_y
        self.heli_x = 100
        self.fire_flag = False
        self.bomb_flag = False
        self.tangagedSURF = None

        self.sprites = {
            'projectiles': [],
            'enemies': [],
            'mig_projectiles': [],
            'hutten': [],
            'sams': [],
            'rls': [],
            'trees': [],
            'trees_damaged': [],
            'bombs': [],
            'flame': [],
            'explosions': [],
            'star_coords': [],
            'slow_stars_coords': [],
            'rockets': [],
            'vezdehod':[]
        }
        self.clear = False

        self.heli_v_y_ = 0.0
        self.v_x = 0.5
        self.enemy_frame_counter = 0
        self.enemy_frame_counter_MAX = 1000
        self.sam_fire_counter = 0
        self.sam_fire_counter_MAX = 500
        self.bomb_init_speed = 0.0035
        self.bullet_speed = 3.5
        self.mig_speed = 0.63
        self.rocket_speed = 0.92
        self.flame_counter_MAX = 25
        self.flame_counter = 0
        self.shl = 0
        self.ammo = {'bombs_left': self.BOMBS_MAX}

        pygame.init()
        self.auxSURF = pygame.Surface((32, 24))
        self.DISPLAYSURF = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption('RETURN TO SAIGON')

        # self.STARSURF = pygame.image.load_extended('star.bmp')
        self.HELISURF = pygame.image.load_extended('copter.png')
        self.RLSSURF = pygame.image.load_extended('rls.png')
        self.MIGSURF = pygame.image.load_extended('Mig15.png')
        self.HUTSURF = pygame.image.load_extended('hut.png')
        self.PALMSURF = pygame.image.load_extended('palmTree.png')
        self.BOMBSURF = pygame.image.load_extended('bomb.png')
        self.FLAMESURF = pygame.image.load_extended('flame.png')
        self.GAMEOVERSURF = pygame.image.load_extended('gameOver.png')
        self.SAMSURF = pygame.image.load_extended('SAM.png')
        self.ROCKETSURF = pygame.image.load_extended('rocket.png')
        self.PALMDAMAGED = pygame.image.load_extended('palmTree_damaged.png')
        self.VEZDESURF = pygame.image.load_extended('vezdehod.png')

        self.start_mission(1)

    def start_mission(self, m):
        self.MC.currentMission = m
        for a in self.MC.missionGoal().keys():
            self.MC.current[a] = 0
        self.endgame_counter = 0
        self.endgame_lost = False
        self.endgame_won = False
        self.WIDTH = 800
        self.HEIGHT = 600
        self.n_big_stars = 40
        self.n_small_stars = 100
        self.heli_y = self.HEIGHT / 2
        self.big_stars_speed = 0.4
        self.small_stars_speed = 0.7
        self.GROUND_SPEED = 0.25
        self.GROUND_Y = 550
        self.TRACER_LENGTH = 20
        self.particle_size = 2
        self.BOMBS_MAX = 8
        self.r = random.Random()
        self.game_over_counter = 0
        self.mission_complete_counter = 0
        self.mission_complete_flag = False

        self.heli_frame_flag = True
        self.up_flag = False
        self.down_flag = False
        self.tangage_flag_up = False
        self.tangage_flag_down = False
        self.tangage_angle = 0
        self.tangage_speed = 0
        self.heli_y_ = self.heli_y
        self.heli_x = 100
        self.fire_flag = False
        self.bomb_flag = False
        self.tangagedSURF = None

        self.sprites = {
            'projectiles': [],
            'enemies': [],
            'mig_projectiles': [],
            'hutten': [],
            'sams': [],
            'rls': [],
            'vezdehod':[],
            'trees': [],
            'trees_damaged': [],
            'bombs': [],
            'flame': [],
            'explosions': [],
            'star_coords': [],
            'slow_stars_coords': [],
            'rockets': []
        }
        self.clear = False

        self.heli_v_y_ = 0.0
        self.v_x = 0.5
        self.enemy_frame_counter = 0
        self.enemy_frame_counter_MAX = 1000
        self.sam_fire_counter = 0
        self.sam_fire_counter_MAX = 500
        self.bomb_init_speed = 0.0035
        self.bullet_speed = 3.5
        self.mig_speed = 0.63
        self.rocket_speed = 0.92
        self.flame_counter_MAX = 25
        self.flame_counter = 0
        self.shl = 0
        self.ammo = {'bombs_left': self.BOMBS_MAX}
        self.populate_sky()
        self.populate_ground()
        self.init_scene()

    def populate_sky(self):
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

    def populate_ground(self):
        for i in range(0, self.WIDTH*13, 48):
            choice = self.r.choice(["hut", "tree", "SAM", "rls","vezde"])
            if choice == "hut":
                self.sprites['hutten'].append((i, self.GROUND_Y - 32))
            elif choice == "tree":
                self.sprites['trees'].append((i, self.GROUND_Y - 64))
            elif choice == "SAM":
                self.sprites['sams'].append((i, self.GROUND_Y - 32))
            elif choice == 'rls':
                self.sprites['rls'].append((i, self.GROUND_Y - 32))
            elif choice == 'vezde':
                self.sprites['vezdehod'].append((i, self.GROUND_Y - 32))

    def fill_black(self):
        # for i in range(self.n_big_stars):
        self.DISPLAYSURF.fill(
            color.Color('Black'),
            pygame.rect.Rect(
                self.DISPLAYSURF.get_rect()
            )
        )

    def init_scene(self):
        for i in range(self.n_big_stars):
            self.DISPLAYSURF.fill(
                color.Color('White'), pygame.rect.Rect(
                    self.sprites['star_coords'][i][0],
                    self.sprites['star_coords'][i][1],
                    2,
                    2)
            )
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
            (self.heli_x, self.heli_y),
            pygame.rect.Rect(0, 0, 32, 24))

    def game_over_animation(self):
        self.DISPLAYSURF.blit(
            self.GAMEOVERSURF,
            pygame.rect.Rect(
                self.WIDTH / 2 - 200,
                -200 + int(self.game_over_counter),
                400,
                200
            )
        )
        if self.game_over_counter < 400:
            self.game_over_counter += 0.5

    def redraw_sprites(self):
        for i in range(self.ammo['bombs_left']):
            self.DISPLAYSURF.blit(self.BOMBSURF, (1 + i * 17, 1))

        row = 0
        for goal in self.MC.missionGoal().keys():
            font = pygame.font.Font(pygame.font.get_default_font(), 16)
            textSurf = font.render("{0} : {1}/{2}".format(goal, self.MC.current[goal], self.MC.missionGoal()[goal]),
                                   False, pygame.color.Color('White'))
            self.DISPLAYSURF.blit(textSurf, pygame.rect.Rect((self.WIDTH - textSurf.get_width(),
                                                              row * textSurf.get_height(), textSurf.get_width(),
                                                              textSurf.get_height())))
            row += 1

        self.sprites['star_coords'] = [
            (divmod(
                float(s[0]) - self.big_stars_speed + 0.02 * self.v_x,
                self.WIDTH
            )[1],
             s[1])
            for s in self.sprites['star_coords']]
        for star in self.sprites['star_coords']:
            self.DISPLAYSURF.fill(
                color.Color('White'),
                pygame.rect.Rect(
                    (int(star[0]),
                     star[1],
                     2,
                     2))
            )

        self.sprites['slow_stars_coords'] = [
            (divmod(
                float(s[0]) - self.small_stars_speed + 0.02 * self.v_x,
                self.WIDTH
            )[1],
             s[1])
            for s in self.sprites['slow_stars_coords']
            ]
        for s in self.sprites['slow_stars_coords']:
            self.DISPLAYSURF.fill(
                color.Color('Yellow'),
                pygame.rect.Rect(
                    int(s[0]),
                    s[1],
                    1,
                    1)
            )

        self.sprites['projectiles'] = [
            (p[0] + self.bullet_speed * math.cos(p[2]), p[1] + self.bullet_speed * math.sin(p[2]), p[2])
            for p in self.sprites['projectiles']
            if p[0] < self.WIDTH + 20
            ]
        for proj in self.sprites['projectiles']:
            pygame.draw.aaline(self.DISPLAYSURF, pygame.Color('White'),
                               (proj[0], proj[1]),
                               (proj[0] + math.cos(proj[2]) * 20, proj[1] + math.sin(proj[2]) * 20))

        flame_to_append = [
            (b[0], self.GROUND_Y - 32) for b in self.sprites['bombs']
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
            (divmod(f[0] - self.GROUND_SPEED + 0.02 * self.v_x + 32, self.WIDTH*13 + 32)[1] - 32, f[1])
            for f in self.sprites['flame']
            ]

        self.sprites['hutten'] = [
            (divmod(h[0] - self.GROUND_SPEED + 0.02 * self.v_x + 32, self.WIDTH*13 + 32)[1] - 32, h[1])
            for h in self.sprites['hutten']
            ]
        self.sprites['trees'] = [
            (divmod(t[0] - self.GROUND_SPEED + 0.02 * self.v_x + 32, self.WIDTH*13 + 32)[1] - 32, t[1])
            for t in self.sprites['trees']
            ]
        self.sprites['trees_damaged'] = [
            (divmod(t[0] - self.GROUND_SPEED + 0.02 * self.v_x + 32, self.WIDTH*13 + 32)[1] - 32, t[1])
            for t in self.sprites['trees_damaged']
            ]
        self.sprites['sams'] = [
            (divmod(s[0] - self.GROUND_SPEED + 0.02 * self.v_x + 32, self.WIDTH*13 + 32)[1] - 32, s[1])
            for s in self.sprites['sams']
            ]
        self.sprites['rls'] = [
            (divmod(s[0] - self.GROUND_SPEED + 0.02 * self.v_x + 32, self.WIDTH * 13 + 32)[1] - 32, s[1])
            for s in self.sprites['rls']
        ]
        self.sprites['vezdehod'] = [
            (divmod(s[0] - self.GROUND_SPEED + 0.02 * self.v_x + 32, self.WIDTH * 13 + 32)[1] - 32, s[1])
            for s in self.sprites['vezdehod']
        ]

        for h in self.sprites['hutten']:
            self.DISPLAYSURF.blit(self.HUTSURF, (int(h[0]), int(h[1])))

        for t in self.sprites['trees']:
            self.DISPLAYSURF.blit(self.PALMSURF, (int(t[0]), int(t[1])))

        for t in self.sprites['trees_damaged']:
            self.DISPLAYSURF.blit(self.PALMDAMAGED, (int(t[0]), int(t[1])))

        for s in self.sprites['sams']:
            self.DISPLAYSURF.blit(
                self.SAMSURF,
                (int(s[0]), int(s[1])))
        for s in self.sprites['rls']:
            self.DISPLAYSURF.blit(
                self.RLSSURF,
                (int(s[0]), int(s[1])))
        for s in self.sprites['vezdehod']:
            self.DISPLAYSURF.blit(
                self.VEZDESURF,
                (int(s[0]), int(s[1])))
        for f in self.sprites['flame']:
            self.DISPLAYSURF.blit(
                self.FLAMESURF,
                (int(f[0]), int(f[1])),
                pygame.rect.Rect(self.shl, 0, 32, 32)
            )


        self.sprites['enemies'] = [
            (e[0] - self.mig_speed + 0.01 * self.v_x, e[1] + 0.22 * (math.sin(e[2]/113.0)), e[2] + 1)
            for e in self.sprites['enemies']
            if e[0] > -32
            ]
        self.sprites['mig_projectiles'] = [
            (e[0] - 0.5 * self.bullet_speed + 0.01 * self.v_x, e[1])
            for e in self.sprites['mig_projectiles']
            if e[0] > -20
            ]
        for mig in self.sprites['enemies']:
            if mig[2] % 300 == 0:
                self.sprites['mig_projectiles'].append((mig[0] - 20, mig[1] + 16))
        for enemy in self.sprites['enemies']:
            self.DISPLAYSURF.blit(
                self.MIGSURF,
                (int(enemy[0]), int(enemy[1]))
            )
        for proj in self.sprites['mig_projectiles']:
            pygame.draw.aaline(self.DISPLAYSURF, pygame.Color('White'),
                               (proj[0], proj[1]),
                               (proj[0] + 20, proj[1]))

        self.sprites['rockets'] = [
            (r[0] - self.rocket_speed + 0.01 * self.v_x, r[1] - self.rocket_speed)
            for r in self.sprites['rockets']
            if (r[0] > -16 and r[1] > -16)
            ]

        for rocket in self.sprites['rockets']:
            self.DISPLAYSURF.blit(
                self.ROCKETSURF,
                (int(rocket[0]), int(rocket[1]))
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
            self.MC.down('enemies')
            self.sprites['projectiles'].remove(p)
            self.sprites['explosions'].append(Explosion(mig[0] + 4, mig[1] + 16, init_v=0.35, n=60, max_frames=300))
            self.sprites['explosions'].append(Explosion(mig[0] + 4, mig[1] + 16, init_v=0.17, n=30, max_frames=180.0))

        for p in self.sprites['projectiles']:
            for tree in self.sprites['trees']:
                if tree[1] + 4 < p[1] < tree[1] - 4 + 64 and tree[0] + 4 < p[0] + 20 < tree[0] + 64:
                    self.sprites['trees_damaged'].append(tree)
                    self.sprites['trees'].remove(tree)

        for e in self.sprites['enemies']:
            if (e[1] - 32 < self.heli_y < e[1] + 24) and (e[0] - 32 < self.heli_x < e[0] + 32):
                self.endgame_lost = True
                self.sprites['explosions'] += [
                    Explosion(self.heli_x + 16, self.heli_y + 12, init_v=0.7, n=250)]
                self.heli_x = -64
                self.heli_y = -64

        for r in self.sprites['rockets']:
            if (r[1] - 32 < self.heli_y < r[1] + 16) and (r[0] - 32 < self.heli_x < r[0] + 16):
                self.endgame_lost = True
                self.sprites['explosions'] += [
                    Explosion(self.heli_x + 16, self.heli_y + 12, init_v=0.7, n=250)
                ]
                self.heli_x = -64
                self.heli_y = -64

        if not self.mission_complete_flag:
            self.mission_complete_flag = True
            for foetype in self.MC.missionGoal().keys():
                if self.MC.missionGoal()[foetype] > self.MC.current[foetype]:
                    self.mission_complete_flag = False
        if self.mission_complete_flag:
            self.mission_complete_counter += 1
        if self.mission_complete_counter == 80:
            self.endgame_won = True


        if not self.endgame_lost:
            self.heli_y_ += self.heli_v_y_
            self.heli_y = int(self.heli_y_)
            self.tangage_angle += self.tangage_speed * 0.1
            self.heli_v_y_ *= 0.9
        if self.heli_frame_flag and not self.endgame_lost:
            x = 32
            self.heli_frame_flag = not self.heli_frame_flag
        elif not self.endgame_lost:
            x = 0
            self.heli_frame_flag = not self.heli_frame_flag
        if self.endgame_lost:
            x = 0

        self.auxSURF.blit(self.HELISURF, pygame.rect.Rect(x, 0, 32, 24))
        self.tangagedSURF = rotate(self.auxSURF, self.tangage_angle)
        if not self.endgame_lost:
            self.DISPLAYSURF.blit(
                self.tangagedSURF,
                (self.heli_x, self.heli_y)
                # pygame.rect.Rect(x, 0, 32, 24)
            )

        else:
            self.game_over_animation()
            pass

    def launch_enemy(self):
        enemy_y = self.r.randint(20, self.GROUND_Y - 64 - 20)
        self.sprites['enemies'].append((self.WIDTH, enemy_y, 50))

    def sam_fire(self, coord_tuple):
        self.sprites['rockets'].append(coord_tuple)

    def drop_bomb(self):
        self.sprites['bombs'].append((self.heli_x, self.heli_y + 24, self.bomb_init_speed))
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
                    if not self.endgame_lost and not self.endgame_won:
                        self.fire_flag = True
                    elif self.endgame_won and not self.MC.currentMission >= len(self.MC.missions):
                        self.MC.currentMission += 1
                        self.start_mission(self.MC.currentMission)
                    else:
                        pygame.quit()
                        sys.exit(0)
                if event.key == K_i:
                    self.endgame_won = True
                if event.key == K_m and self.ammo.get('bombs_left') > 0:
                    self.bomb_flag = True
                if event.key == K_d:
                    self.tangage_flag_up = True
                    self.tangage_flag_down = False
                if event.key == K_a:
                    self.tangage_flag_up = False
                    self.tangage_flag_down = True

            if event.type == KEYUP:
                if event.key == K_s:
                    self.down_flag = False
                if event.key == K_w:
                    self.up_flag = False
                if event.key == K_d:
                    self.tangage_flag_up = False
                if event.key == K_a:
                    self.tangage_flag_down = False


    def launch_victory_fireworks(self):
        self.game_over_counter += 1

        if self.game_over_counter >= 200:
            self.sprites['explosions'].append(
                Explosion(
                    self.r.randint(0, self.WIDTH),
                    self.r.randint(0, self.HEIGHT), n=40, v_x=0, init_v=0.6
                ))
            self.game_over_counter = 0

    def clear_sprites(self):
        self.sprites['projectiles'] = []
        self.sprites['enemies'] = []
        self.sprites['mig_projectiles'] = []
        self.sprites['hutten'] = []
        self.sprites['trees'] = []
        self.sprites['bombs'] = []
        self.sprites['flame'] = []
        self.sprites['sams'] = []
        self.sprites['rockets'] = []
        # self.sprites['explosions'] = []
        self.sprites['star_coords'] = []
        self.sprites['slow_stars_coords'] = []
        self.clear = True
        self.heli_y_ = -32
        self.ammo['bombs_left'] = 0

    def loop(self):
        self.init_scene()
        while True:
            self.end = self.endgame_won or self.endgame_lost
            self.flame_counter += 1
            self.enemy_frame_counter += 1
            self.sam_fire_counter += 1
            if self.enemy_frame_counter == self.enemy_frame_counter_MAX:
                self.launch_enemy()
                self.enemy_frame_counter = 0
            if self.sam_fire_counter == self.sam_fire_counter_MAX and len(self.sprites['sams']) > 0:
                self.sam_fire(self.r.choice(self.sprites['sams']))
                self.sam_fire_counter = 0
            if self.flame_counter == self.flame_counter_MAX:
                self.flame_counter = 0
                self.shl = 32 - self.shl
            if self.up_flag and not self.end:
                self.heli_v_y_ -= 0.015
            if self.down_flag and not self.end:
                self.heli_v_y_ += 0.015
            if self.fire_flag and not self.end:
                self.sprites['projectiles'].append((100, self.heli_y, -self.tangage_angle / 180 * math.pi))
                self.fire_flag = not self.fire_flag
            if self.bomb_flag and not self.end:
                self.drop_bomb()
                self.bomb_flag = not self.bomb_flag
            if self.tangage_flag_up:
                self.tangage_speed += 0.5
                # self.v_x += 0.05
            elif self.tangage_flag_down:
                self.tangage_speed -= 0.5
                # self.v_x -= 0.05
            else:
                self.tangage_speed *= 0.95
                self.tangage_angle *= 0.98

            self.v_x = 0.5 + self.tangage_angle

            self.tangage_speed = self.tangage_speed * 0.7  # - self.tangage_angle*0.02


            self.fill_black()

            self.process_events()

            self.redraw_sprites()
            if self.endgame_won:
                if not self.clear:
                    self.clear_sprites()
                self.launch_victory_fireworks()


            pygame.display.update()


game = Game()
game.loop()
