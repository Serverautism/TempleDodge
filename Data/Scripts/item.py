import pygame
from random import randint


class Item:
    def __init__(self, name, center, velocity, landed_rocks):
        self.name = name
        self.center = center
        self.velocity = velocity
        self.landed_rocks = landed_rocks
        self.frames_count = 0
        self.frames_change = 0.2
        self.frame = randint(0, 5)

        if self.name == 'mana':
            self.frames_len = 15
            path = 'Data/Assets/Sprites/Items/Mana/mana_'
        elif self.name == 'gold':
            self.frames_len = 15
            path = 'Data/Assets/Sprites/Items/Coin/gold_'

        self.frames = []
        for i in range(self.frames_len):
            image = pygame.image.load(path + f'{i + 1}.png').convert_alpha()
            self.frames.append(image)

        self.image = self.frames[self.frame]
        self.rect = self.image.get_rect()
        self.rect.center = self.center
        self.mask = pygame.mask.from_surface(self.image)

    def update(self, surface):
        # move left right, check collision
        self.rect.x += self.velocity[0]
        self.check_collision_x()

        # move up down, check collision
        self.rect.y += self.velocity[1]
        self.check_collision_y()

    def check_collision_x(self):
        pass

    def check_collision_y(self):
        pass


