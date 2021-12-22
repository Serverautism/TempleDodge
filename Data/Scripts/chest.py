import pygame
from random import randint


from . import item


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
        elif self.name == 'mana':
            self.drop_count = 1

    def update(self, surface,  all_rocks):
        if not self.crushed:
            for entity in all_rocks:
                if self.rect.colliderect(entity.rect):
                    self.crush()

            self.rect.bottom = self.rock.rect.top

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
        # spawn particles
