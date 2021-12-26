import pygame


class Rock:
    def __init__(self, render_pos, speed, landed):
        self.x, self.y = render_pos
        self.speed = speed
        self.landed = landed

        self.image = pygame.image.load('Data/Assets/Sprites/Rock/rock.png').convert_alpha()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y

    def update(self, surface, paused, landed_rocks=None):
        if not self.landed and not paused:
            self.rect.y += self.speed
            for entity in landed_rocks:
                if self.rect.colliderect(entity.rect):
                    self.rect.bottom = entity.rect.top
                    self.landed = True

        surface.blit(self.image, self.rect)

    def move_down(self, pixels):
        self.rect.y += pixels
