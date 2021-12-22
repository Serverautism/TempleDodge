import pygame
from random import randint


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

        if self.name == 'mana':
            self.frames_len = 15
            path = 'Data/Assets/Sprites/Items/Mana/mana_'
        elif self.name == 'gold':
            self.frames_len = 15
            path = 'Data/Assets/Sprites/Items/Gold/gold_'

        self.frames = []
        for i in range(self.frames_len):
            image = pygame.image.load(path + f'{i + 1}.png').convert_alpha()
            self.frames.append(image)

        self.image = self.frames[self.frame]
        self.rect = self.image.get_rect()
        self.rect.center = self.center
        self.mask = pygame.mask.from_surface(self.image)

    def update(self, surface):
        # get image
        self.get_image()

        # move left right, check collision
        self.rect.x += self.velocity[0]
        self.check_collision_x()

        # move up down, check collision
        self.rect.y += self.velocity[1]
        self.check_collision_y()
        self.apply_gravity()

        # blit
        surface.blit(self.image, self.rect)

    def check_collision_x(self):
        landed_rock_hit_list = pygame.sprite.spritecollide(self, self.landed_rocks, False)
        for entity in landed_rock_hit_list:
            if self.velocity[0] > 0:
                self.rect.right = entity.rect.left
            elif self.velocity[0] < 0:
                self.rect.left = entity.rect.right
            self.velocity[0] *= -.75

    def check_collision_y(self):
        landed_rock_hit_list = pygame.sprite.spritecollide(self, self.landed_rocks, False)
        if len(landed_rock_hit_list) > 0:
            if self.velocity[1] != 0:
                if self.gravity * -2 < self.velocity[1] < self.gravity * 2:
                    self.velocity[1] = 0
                else:
                    self.rect.y -= self.velocity[1]
            self.velocity[1] *= -.25

        falling_rock_hit_list = pygame.sprite.spritecollide(self, self.falling_rocks, False)
        if len(falling_rock_hit_list) > 0:
            if self.velocity[1] <= 0:
                self.collected = True
            else:
                self.rect.y -= self.velocity[1]
                self.velocity[1] *= -.25

    def apply_gravity(self):
        if self.velocity[1] != 0:
            self.velocity[1] += self.gravity

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

