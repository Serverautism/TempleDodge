import pygame
from random import randint
import time
import math


from . import item
from . import particle
from . import funcs


class Chest:
    def __init__(self, rock, name, landed_rocks, falling_rocks):
        self.rock = rock
        self.name = name
        self.landed_rocks = landed_rocks
        self.falling_rocks = falling_rocks
        self.closed_image = pygame.image.load(f'Data/Assets/Sprites/Chest/chest_{self.name}_1.png').convert_alpha()
        self.open_image = pygame.image.load(f'Data/Assets/sprites/Chest/chest_{self.name}_2.png').convert_alpha()
        self.rect = self.closed_image.get_rect()
        self.rect.bottom = self.rock.rect.top
        self.rect.x = self.rock.rect.x
        self.opened = False
        self.crushed = False
        self.done = False
        self.particles = []
        self.items = []
        
        if self.name == 'gold':
            self.drop_count = 5
            self.death_particle_color = (110, 97, 0)
            self.death_particle_glow_color = (5, 4, 0)
        elif self.name == 'mana':
            self.drop_count = 1
            self.death_particle_color = (0, 74, 112)
            self.death_particle_glow_color = (0, 4, 6)

        self.dt = 0
        self.last_time = time.time()

        self.particles = []

        self.death_particle_ammount = 60
        self.death_particle_speed = 5

    def update(self, surface,  all_rocks):
        if not self.crushed:
            # determine delta time
            self.dt = time.time() - self.last_time
            self.dt *= 60
            self.last_time = time.time()

            self.rect.bottom = self.rock.rect.top

            for entity in all_rocks:
                if self.rect.colliderect(entity.rect):
                    self.crush()

            if self.opened:
                surface.blit(self.open_image, self.rect)
            else:
                surface.blit(self.closed_image, self.rect)

        else:
            if len(self.particles) <= 0:
                self.done = True

        if self.rect.y >= 288:
            self.done = True

    def open(self):
        if not self.opened:
            self.opened = True

            for i in range(self.drop_count):
                velocity = [randint(0, 40)/10 - 2, -1]
                self.items.append(item.Item(self.name, [self.rect.center[0], self.rect.top], velocity, self.landed_rocks, self.falling_rocks))

    def crush(self):
        self.crushed = True
        self.add_death_particles()

    def add_death_particles(self):
        for i in range(self.death_particle_ammount):
            center = list(funcs.render_pos_to_screen_pos(self.rect.center, (1920, 1080)))
            radians = math.radians((360 / self.death_particle_ammount) * i)
            velocity = [self.death_particle_speed * math.cos(radians) + (randint(1, 10) / 10 - .5), self.death_particle_speed * math.sin(radians) + (randint(1, 10) / 10 - .5)]
            radius = randint(1, 5)
            lifetime = 2

            p = particle.Particle(center, velocity, radius, lifetime, self.death_particle_color, self.death_particle_glow_color, has_glow=True, gravity=.4)
            self.particles.append(p)

    def update_particles(self, surface):
        to_remove = []
        for entity in self.particles:
            if entity.dead:
                to_remove.append(entity)
            else:
                entity.update(surface)

        for entity in to_remove:
            self.particles.remove(entity)
