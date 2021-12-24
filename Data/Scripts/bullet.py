import pygame


class Bullet:
    def __init__(self, velocity, position):
        self.velocity = velocity
        self.image = pygame.image.load('Data/Assets/Sprites/Bullets/bullet.png').convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.center = position
        self.sparkle_frames_length = 8

        self.glow_color = (20, 0, 44)

        self.big_glow_size = self.rect.width * 2
        self.small_glow_size = self.rect.width * 1.5

        self.glow_grow = True
        self.dead = True

        self.sparkle_frames = []
        for i in range(self.sparkle_frames_length):
            image = pygame.image.load(f'Data/Assets/Sprites/Bullets/sparkle_{i + 1}.png').convert_alpha()
            self.sparkle_frames.append(image)

    def update(self, surface):
        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]

        glow_big, glow_small = self.get_glow()

        surface.blit(glow_big, self.rect.center, special_flags=pygame.BLEND_RGB_ADD)
        surface.blit(glow_small, self.rect.center, special_flags=pygame.BLEND_RGB_ADD)
        surface.blit(self.image, self.rect.center)

    def get_glow(self):
        if self.glow_grow:
            if self.big_glow_size >= self.rect.width * 3:
                self.glow_grow = False

            self.big_glow_size += 1
            self.small_glow_size += 1
        else:
            if self.big_glow_size <= self.rect.width * 2:
                self.glow_grow = True

            self.big_glow_size -= 1
            self.small_glow_size -= 1

        big_glow_surface = pygame.Surface((self.big_glow_size * 2, self.big_glow_size * 2))
        big_glow_surface.set_colorkey((0, 0, 0))
        small_glow_surface = pygame.Surface((self.small_glow_size * 2, self.small_glow_size * 2))
        small_glow_surface.set_colorkey((0, 0, 0))

        pygame.draw.circle(big_glow_surface, self.glow_color, (self.big_glow_size, self.big_glow_size), self.big_glow_size)
        pygame.draw.circle(small_glow_surface, self.glow_color, (self.small_glow_size, self.small_glow_size), self.small_glow_size)

        return big_glow_surface, small_glow_surface

