import pygame
import math
from random import randint
import time


from . import particle
from . import funcs


class Bullet:
    def __init__(self, velocity, position, wall):
        self.velocity = velocity
        self.position = position
        self.wall = wall
        self.image = pygame.image.load('Data/Assets/Sprites/Bullets/bullet.png').convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.center = position
        self.sparkle_frames_length = 8
        self.frame = 0
        self.frame_change = .1
        self.frame_count = 0

        radians = math.atan2(*velocity)
        self.angle = math.degrees(radians)
        self.angle -= 90

        self.glow_color = (20, 0, 44)

        self.big_glow_size = self.rect.width * 2
        self.small_glow_size = self.rect.width

        self.glow_grow = True
        self.dead = False
        self.sparkle_done = False

        self.sparkle_frames = []
        for i in range(self.sparkle_frames_length):
            image = pygame.image.load(f'Data/Assets/Sprites/Bullets/Sparkle/sparkle_{i + 1}.png').convert_alpha()

            if self.wall == 2:
                self.sparkle_frames.append(pygame.transform.rotate(image, self.angle + 180))
            elif self.wall == 1:
                self.sparkle_frames.append(pygame.transform.rotate(image, self.angle + 180))
            else:
                self.sparkle_frames.append(pygame.transform.rotate(image, self.angle + 180))

        self.sparkle_image = self.sparkle_frames[0]

        if self.wall == 0:
            self.render_x = int(position[0] - abs(self.angle) / 2)
            self.render_y = int(position[1] - self.sparkle_image.get_height() / 2)
        elif self.wall == 1:
            self.render_x = int(position[0] - self.sparkle_image.get_width() / 2)
            self.render_y = int(position[1] - abs(self.angle) / 2)
        else:
            self.render_x = int(position[0] - self.sparkle_image.get_width() * .75)
            self.render_y = int(position[1] - self.sparkle_image.get_height() / 2)

        self.particles = []

        self.move_particle_time = 5
        self.move_particle_count = 0
        self.move_particle_color = (131, 31, 255)
        self.move_particle_glow_color = (5, 0, 11)

        self.dt = 0
        self.last_time = time.time()

    def update(self, surface, paused):
        # calc delta time
        self.dt = time.time() - self.last_time
        self.dt *= 60
        self.last_time = time.time()
        if not paused:
            # move
            self.position[0] += self.velocity[0] * self.dt
            self.position[1] += self.velocity[1] * self.dt
            self.rect.center = self.position

            self.check_dead()

        if not self.dead:

            glow_big, glow_small = self.get_glow()

            surface.blit(glow_big, (self.rect.center[0] - glow_big.get_width() / 2, self.rect.center[1] - glow_big.get_height() / 2), special_flags=pygame.BLEND_RGB_ADD)
            surface.blit(glow_small, (self.rect.center[0] - glow_small.get_width() / 2, self.rect.center[1] - glow_small.get_height() / 2), special_flags=pygame.BLEND_RGB_ADD)
            surface.blit(self.image, self.rect)

        if not self.sparkle_done:
            self.draw_sparkle(surface)

    def get_glow(self):
        if self.glow_grow:
            self.big_glow_size += 1 * self.dt
            self.small_glow_size += 1 * self.dt

            if self.big_glow_size >= self.rect.width * 3:
                self.glow_grow = False

        else:
            self.big_glow_size -= 1 * self.dt
            self.small_glow_size -= 1 * self.dt

            if self.big_glow_size <= self.rect.width * 2:
                self.glow_grow = True
                self.big_glow_size = self.rect.width * 2
                self.small_glow_size = self.rect.width

        big_glow_surface = pygame.Surface((self.big_glow_size * 2, self.big_glow_size * 2))
        big_glow_surface.set_colorkey((0, 0, 0))
        small_glow_surface = pygame.Surface((self.small_glow_size * 2, self.small_glow_size * 2))
        small_glow_surface.set_colorkey((0, 0, 0))

        pygame.draw.circle(big_glow_surface, self.glow_color, (self.big_glow_size, self.big_glow_size), self.big_glow_size)
        pygame.draw.circle(small_glow_surface, self.glow_color, (self.small_glow_size, self.small_glow_size), self.small_glow_size)

        return big_glow_surface, small_glow_surface

    def check_dead(self):
        if self.rect.center[0] + self.big_glow_size < 0:
            self.dead = True
        elif self.rect.center[0] - self.big_glow_size > 512:
            self.dead = True
        elif self.rect.center[1] + self.big_glow_size < 0:
            self.dead = True
        elif self.rect.center[1] - self.big_glow_size > 288:
            self.dead = True

    def draw_sparkle(self, surface):
        self.frame_count += 1
        if self.frame_count / 60 >= self.frame_change:
            self.frame_count = 0
            self.frame += 1

            if self.frame == self.sparkle_frames_length - 1:
                self.sparkle_done = True
                return

            self.sparkle_image = self.sparkle_frames[self.frame]

        surface.blit(self.sparkle_image, (self.render_x, self.render_y))

    def update_particles(self, surface):
        # spawn particle
        self.move_particle_count += 1
        if self.move_particle_count == self.move_particle_time:
            self.move_particle_count = 0

            center = list(funcs.render_pos_to_screen_pos(self.rect.center, (1920, 1080)))
            velocity = [randint(1, 20) / 10 - 1, randint(1, 20) / 10 - 1]
            radius = randint(1, 3)
            lifetime = 2

            p = particle.Particle(center, velocity, radius, lifetime, self.move_particle_color, self.move_particle_glow_color, has_glow=True)
            self.particles.append(p)

        # update_particles
        to_remove = []
        for entity in self.particles:
            if entity.dead:
                to_remove.append(entity)
            else:
                entity.update(surface)

        for entity in to_remove:
            self.particles.remove(entity)

