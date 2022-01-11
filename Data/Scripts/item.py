import pygame
from random import randint
import time


from . import particle
from . import funcs


class Item:
    def __init__(self, name, center, velocity, landed_rocks, falling_rocks):
        self.name = name
        self.center = center
        self.velocity = velocity
        self.gravity = 0.2
        self.landed_rocks = landed_rocks
        self.falling_rocks = falling_rocks
        self.frames_count = 0
        self.frames_change = 0.2
        self.frame = randint(0, 5)
        self.collected = False
        self.collectable = False
        self.collectable_delay = 20
        self.collectable_delay_count = 0

        self.particles = []

        self.move_particle_time = 10
        self.move_particle_count = 0

        self.left_border_rect = pygame.rect.Rect(0, 0, 16, 288)
        self.right_border_rect = pygame.rect.Rect(512 - 16, 0, 16, 288)

        if self.name == 'mana':
            self.frames_len = 15
            path = 'Data/Assets/Sprites/Items/Mana/mana_'
            self.move_particle_color = (129, 212, 250)
            self.move_particle_glow_color = (0, 8, 11)
        elif self.name == 'gold':
            self.frames_len = 15
            path = 'Data/Assets/Sprites/Items/Gold/gold_'
            self.move_particle_color = (224, 192, 95)
            self.move_particle_glow_color = (14, 10, 0)

        self.frames = []
        for i in range(self.frames_len):
            image = pygame.image.load(path + f'{i + 1}.png').convert_alpha()
            self.frames.append(image)

        self.image = self.frames[self.frame]
        self.rect = self.image.get_rect()
        self.rect.center = self.center
        self.mask = pygame.mask.from_surface(self.image)

        self.dt = 0
        self.last_time = time.time()

    def update(self, surface, paused):
        # calculate delta time
        self.dt = time.time() - self.last_time
        self.dt *= 60
        self.last_time = time.time()

        # get image
        self.get_image()

        if not paused:
            # check if collectable
            if not self.collectable:
                self.check_collectable()

            # move left right, check collision
            self.center[0] += self.velocity[0] * self.dt
            self.rect.centerx = self.center[0]
            self.check_collision_x()

            # move up down, check collision
            self.center[1] += self.velocity[1] * self.dt
            self.rect.centery = self.center[1]
            self.check_collision_y()
            self.apply_gravity()

        # blit
        surface.blit(self.image, self.rect)

    def check_collision_x(self):
        landed_rock_hit_list = pygame.sprite.spritecollide(self, self.landed_rocks, False)
        if len(landed_rock_hit_list) > 0:
            self.center[0] -= self.velocity[0] * self.dt
            self.rect.centerx = self.center[0]

            self.velocity[0] *= -.75

        falling_rock_hit_list = pygame.sprite.spritecollide(self, self.falling_rocks, False)
        if len(falling_rock_hit_list) > 0:
            if self.velocity[0] != 0:
                self.center[0] -= self.velocity[0] * self.dt
                self.rect.centerx = self.center[0]
            self.velocity[0] *= -.75

        if self.rect.colliderect(self.left_border_rect):
            self.rect.left = self.left_border_rect.right
            self.center = list(self.rect.center)
            self.velocity[0] *= -.75

        if self.rect.colliderect(self.right_border_rect):
            self.rect.right = self.right_border_rect.left
            self.center = list(self.rect.center)
            self.velocity[0] *= -.75

    def check_collision_y(self):
        landed_rock_hit_list = pygame.sprite.spritecollide(self, self.landed_rocks, False)
        if len(landed_rock_hit_list) > 0:
            if self.velocity[1] != 0:
                self.center[1] -= self.velocity[1] * self.dt
                self.rect.centery = self.center[1]
            self.velocity[1] *= -.25

        falling_rock_hit_list = pygame.sprite.spritecollide(self, self.falling_rocks, False)
        for entity in falling_rock_hit_list:
            if self.rect.y >= entity.rect.y:
                self.collected = True
            else:
                self.center[1] -= self.velocity[1] * self.dt
                self.rect.centery = self.center[1]
                self.velocity[1] *= -.25

    def apply_gravity(self):
        if self.velocity[1] != 0:
            self.velocity[1] += self.gravity * self.dt

    def check_collectable(self):
        self.collectable_delay_count += 1
        if self.collectable_delay_count >= self.collectable_delay:
            self.collectable = True

    def collect(self):
        self.collected = True

    def get_image(self):
        self.frames_count += 1
        if self.frames_count / 60 >= self.frames_change:
            self.frames_count = 0
            self.frame += 1
            if self.frame > self.frames_len - 1:
                self.frame = 0

        self.image = self.frames[self.frame]
        self.mask = pygame.mask.from_surface(self.image)

    def update_particles(self, surface):
        # spawn particle
        self.move_particle_count += 1 * self.dt
        if self.move_particle_count >= self.move_particle_time:
            self.move_particle_count = 0

            center = list(funcs.render_pos_to_screen_pos(self.rect.center, (1920, 1080)))
            velocity = [randint(1, 10) / 10 - .5, randint(1, 10) / 10 - .5]
            radius = randint(1, 3)
            lifetime = 1

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


