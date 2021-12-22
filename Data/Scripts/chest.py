import pygame


class Chest:
    def __init__(self, rock, item):
        self.rock = rock
        self.item = item
        self.closed_image = pygame.image.load(f'Data/Assets/Sprites/Chest/chest_{self.item}_1.png').convert_alpha()
        self.open_image = pygame.image.load(f'Data/Assets/sprites/Chest/chest_{self.item}_2.png').convert_alpha()
        self.rect = self.closed_image.get_rect()
        self.rect.bottom = self.rock.rect.top
        self.rect.x = self.rock.rect.x
        self.opened = False
        self.crushed = False
        self.done = False
        self.particles = []
        self.items = []
        self.mana_drop_count = 1
        self.gold_drop_count = 5

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

        for entity in self.particles:
            entity.update()

    def open(self):
        self.opened = True

    def crush(self):
        self.crushed = True
        # spawn particles
