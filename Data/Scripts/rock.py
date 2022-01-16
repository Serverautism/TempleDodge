import pygame
from random import randint
import time


from . import particle
from . import funcs


class Rock:
    def __init__(self, render_pos, speed, landed, landed_rocks, width: int = 1):
        self.x, self.y = render_pos
        self.speed = speed
        self.landed = landed
        self.landed_rocks = landed_rocks

        self.width = width

        self.last_time = time.time()
        self.dt = 0

        if width == 1:
            self.image = pygame.image.load('Data/Assets/Sprites/Rock/rock.png').convert_alpha()
        elif width == 2:
            self.image = pygame.image.load('Data/Assets/Sprites/Rock/rock_wide.png').convert_alpha()

        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y

        self.particles = []

        self.particle_time = 10
        self.particle_count = 0
        self.particle_color = (226, 156, 255)
        self.particle_glow_color = (6, 0, 8)

    def update(self, surface, paused):
        if not self.landed and not paused:
            # determine delta time
            self.dt = time.time() - self.last_time
            self.dt *= 60
            self.last_time = time.time()

            self.y += self.speed * self.dt
            self.rect.y = self.y
            for entity in self.landed_rocks:
                if entity.rect.x <= self.rect.x <= entity.rect.right:
                    if self.rect.colliderect(entity.rect):
                        self.rect.bottom = entity.rect.top
                        self.y = self.rect.top
                        self.landed = True

        surface.blit(self.image, self.rect)

    def move_down(self, pixels):
        self.y += pixels
        self.rect.y = self.y

    def update_particles(self, surface):
        if not self.landed:
            self.particle_count += 1 * self.dt
            if self.particle_count >= self.particle_time:
                self.particle_count = 0

                center_1 = list(funcs.render_pos_to_screen_pos(self.rect.topleft, (1920, 1080)))
                center_2 = list(funcs.render_pos_to_screen_pos(self.rect.topright, (1920, 1080)))
                velocity_1 = [randint(-5, 5) / 10, randint(0, 10) / 10 - .5]
                velocity_2 = [randint(-5, 5) / 10, randint(0, 10) / 10 - .5]
                radius_1 = randint(1, 3)
                radius_2 = randint(1, 3)
                lifetime = 1

                self.particles.append(particle.Particle(center_1, velocity_1, radius_1, lifetime, self.particle_color, self.particle_glow_color, has_glow=True))
                self.particles.append(particle.Particle(center_2, velocity_2, radius_2, lifetime, self.particle_color, self.particle_glow_color, has_glow=True))

        to_remove = []
        for entity in self.particles:
            if entity.dead:
                to_remove.append(entity)
            else:
                entity.update(surface)

        for entity in to_remove:
            self.particles.remove(entity)

