import pygame
from random import randint
import time


from . import particle
from . import funcs


# this object represents one rock
class Rock:
    # set its attributes
    def __init__(self, render_pos, speed, landed, landed_rocks, width: int = 1):
        self.x, self.y = render_pos
        self.speed = speed
        self.landed = landed
        self.landed_rocks = landed_rocks

        # how many blocks its wide
        self.width = width

        # keep track of the time between two frames
        self.last_time = time.time()
        self.dt = 0

        # load the rocks image based on its width
        if width == 1:
            self.image = pygame.image.load('Data/Assets/Sprites/Rock/rock.png').convert_alpha()
        elif width == 2:
            self.image = pygame.image.load('Data/Assets/Sprites/Rock/rock_wide.png').convert_alpha()

        # set mask and rect for collision
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y

        self.particles = []

        # variables for spawning particles
        self.particle_time = 10
        self.particle_count = 0
        self.particle_color = (226, 156, 255)
        self.particle_glow_color = (6, 0, 8)

    # main update function
    def update(self, surface, paused):
        # determine delta time since last frame
        self.dt = time.time() - self.last_time
        self.dt *= 60
        self.last_time = time.time()

        # if the game is not paused and the rock did not already landed
        if not self.landed and not paused:
            # move the rock
            self.y += self.speed * self.dt
            self.rect.y = self.y

            # and check if the rock collides with a rock under its position
            for entity in self.landed_rocks:
                if entity.rect.x <= self.rect.x <= entity.rect.right:
                    if self.rect.colliderect(entity.rect):
                        # if so sets its position on top of the rock and set itself to landed
                        self.rect.bottom = entity.rect.top
                        self.y = self.rect.top
                        self.landed = True

        # draw its image
        surface.blit(self.image, self.rect)

    # changes to rock position and rect on the y-axis
    def move_down(self, pixels):
        self.y += pixels
        self.rect.y = self.y

    # updates the particles and spawns some on the top left and right corners
    def update_particles(self, surface):
        if not self.landed:
            # spawn particle only if falling
            self.particle_count += 1 * self.dt
            if self.particle_count >= self.particle_time:
                self.particle_count = 0

                # if its time to spawn a particle set the attributes for a particle on the left and one on the right corner
                center_1 = list(funcs.render_pos_to_screen_pos(self.rect.topleft, (1920, 1080)))
                center_2 = list(funcs.render_pos_to_screen_pos(self.rect.topright, (1920, 1080)))
                velocity_1 = [randint(-5, 5) / 10, randint(0, 10) / 10 - .5]
                velocity_2 = [randint(-5, 5) / 10, randint(0, 10) / 10 - .5]
                radius_1 = randint(1, 3)
                radius_2 = randint(1, 3)
                lifetime = 1

                # create these two particles and add them to the list
                self.particles.append(particle.Particle(center_1, velocity_1, radius_1, lifetime, self.particle_color, self.particle_glow_color, has_glow=True))
                self.particles.append(particle.Particle(center_2, velocity_2, radius_2, lifetime, self.particle_color, self.particle_glow_color, has_glow=True))

        # update all particles and remove them if they are dead
        to_remove = []
        for entity in self.particles:
            if entity.dead:
                to_remove.append(entity)
            else:
                entity.update(surface)

        for entity in to_remove:
            self.particles.remove(entity)

