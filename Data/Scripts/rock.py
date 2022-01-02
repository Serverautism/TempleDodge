import pygame
from random import randint


from . import particle


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

        self.particles = []

        self.particle_time = 10
        self.particle_count = 0
        self.particle_color = (226, 156, 255)
        self.particle_glow_color = (11, 0, 16)

    def update(self, surface, paused, landed_rocks=None):
        if not self.landed and not paused:
            self.rect.y += self.speed
            for entity in landed_rocks:
                if self.rect.colliderect(entity.rect):
                    self.rect.bottom = entity.rect.top
                    self.landed = True

            self.handle_particles(surface)

        surface.blit(self.image, self.rect)

    def move_down(self, pixels):
        self.rect.y += pixels

    def handle_particles(self, surface):
        self.particle_count += 1
        if self.particle_count == self.particle_time:
            self.particle_count = 0

            center_1 = list(self.rect.topleft)
            center_2 = list(self.rect.topright)
            velocity_1 = [randint(0, 10) / 10 - .5, 0]
            velocity_2 = [randint(0, 10) / 10 - .5, 0]
            radius_1 = 1
            radius_2 = 1
            lifetime = 1

            self.particles.append(particle.Particle(center_1, velocity_1, radius_1, lifetime, self.particle_color, self.particle_glow_color, static_size=True, has_glow=True))
            self.particles.append(particle.Particle(center_2, velocity_2, radius_2, lifetime, self.particle_color, self.particle_glow_color, static_size=True, has_glow=True))

        to_remove = []
        for entity in self.particles:
            if entity.dead:
                to_remove.append(entity)
            else:
                entity.update(surface)

        for entity in to_remove:
            self.particles.remove(entity)

