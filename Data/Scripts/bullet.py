import pygame
import math
from random import randint
import time


from . import particle
from . import funcs


# represents one of the purple projectiles in game
class Bullet:
    # set its parameters
    def __init__(self, velocity, position, wall):
        self.velocity = velocity
        self.position = position

        # wall index to determine the wall to draw the sparkles on
        # sparkle means shooting effect
        self.wall = wall
        self.image = pygame.image.load('Data/Assets/Sprites/Bullets/bullet.png').convert_alpha()

        # its hit box
        self.rect = self.image.get_rect()
        self.rect.center = position

        self.sparkle_frames_length = 8
        self.frame = 0
        self.frame_change = .1
        self.frame_count = 0

        # calculate the angle by its velocity to rotate the sparkle images later
        radians = math.atan2(*velocity)
        self.angle = math.degrees(radians)
        self.angle -= 90

        self.glow_color = (20, 0, 44)

        # set the sizes of the glow around the bullet
        self.big_glow_size = self.rect.width * 2
        self.small_glow_size = self.rect.width

        self.glow_grow = True
        self.dead = False
        self.sparkle_done = False

        # load the frames for the sparkle effect
        self.sparkle_frames = []
        for i in range(self.sparkle_frames_length):
            image = pygame.image.load(f'Data/Assets/Sprites/Bullets/Sparkle/sparkle_{i + 1}.png').convert_alpha()

            # rotate the image based on the wall the bullet is coming from
            # and the bullets velocity to match the bullets direction
            if self.wall == 2:
                self.sparkle_frames.append(pygame.transform.rotate(image, self.angle + 180))
            elif self.wall == 1:
                self.sparkle_frames.append(pygame.transform.rotate(image, self.angle + 180))
            else:
                self.sparkle_frames.append(pygame.transform.rotate(image, self.angle + 180))

        self.sparkle_image = self.sparkle_frames[0]

        # move the sparkle effect render position based on its rotation
        if self.wall == 0:
            self.render_x = int(position[0] - abs(self.angle) / 2)
            self.render_y = int(position[1] - self.sparkle_image.get_height() / 2)
        elif self.wall == 1:
            self.render_x = int(position[0] - self.sparkle_image.get_width() / 2)
            self.render_y = int(position[1] - abs(self.angle) / 2)
        else:
            self.render_x = int(position[0] - self.sparkle_image.get_width() * .75)
            self.render_y = int(position[1] - self.sparkle_image.get_height() / 2)

        self.particles = []

        # values for generating particles
        self.move_particle_time = 5
        self.move_particle_count = 0
        self.move_particle_color = (131, 31, 255)
        self.move_particle_glow_color = (5, 0, 11)

        # delta time between frames
        self.dt = 0
        self.last_time = time.time()

    # main update function
    def update(self, surface, paused):
        # calculate the delta time
        self.dt = time.time() - self.last_time
        self.dt *= 60
        self.last_time = time.time()

        # if the ga,e is not paused
        if not paused:
            # move the bullets position based on its speed and set its hit box position
            self.position[0] += self.velocity[0] * self.dt
            self.position[1] += self.velocity[1] * self.dt
            self.rect.center = self.position

            # then check if the bullet is off the screen
            self.check_dead()

        if not self.dead:
            # get the glow images
            glow_big, glow_small = self.get_glow()

            # draw the glow and the bullet image to the surface
            # the position is based on the glows size
            surface.blit(glow_big, (self.rect.center[0] - glow_big.get_width() / 2, self.rect.center[1] - glow_big.get_height() / 2), special_flags=pygame.BLEND_RGB_ADD)
            surface.blit(glow_small, (self.rect.center[0] - glow_small.get_width() / 2, self.rect.center[1] - glow_small.get_height() / 2), special_flags=pygame.BLEND_RGB_ADD)
            surface.blit(self.image, self.rect)

        # if the shooting animation is still going
        # draw it
        if not self.sparkle_done:
            self.draw_sparkle(surface)

    # returns the surfaces holding the images for the glow
    def get_glow(self):
        # change the glows size to get the pulsating effect
        # make it bigger
        if self.glow_grow:
            self.big_glow_size += 1 * self.dt
            self.small_glow_size += 1 * self.dt

            if self.big_glow_size >= self.rect.width * 3:
                self.glow_grow = False
        # or smaller
        else:
            self.big_glow_size -= 1 * self.dt
            self.small_glow_size -= 1 * self.dt

            if self.big_glow_size <= self.rect.width * 2:
                self.glow_grow = True
                self.big_glow_size = self.rect.width * 2
                self.small_glow_size = self.rect.width

        # create new surfaces based on the size of the glow
        big_glow_surface = pygame.Surface((self.big_glow_size * 2, self.big_glow_size * 2))
        big_glow_surface.set_colorkey((0, 0, 0))
        small_glow_surface = pygame.Surface((self.small_glow_size * 2, self.small_glow_size * 2))
        small_glow_surface.set_colorkey((0, 0, 0))

        # and draw purple circles onto the surface for the glow
        pygame.draw.circle(big_glow_surface, self.glow_color, (self.big_glow_size, self.big_glow_size), self.big_glow_size)
        pygame.draw.circle(small_glow_surface, self.glow_color, (self.small_glow_size, self.small_glow_size), self.small_glow_size)

        return big_glow_surface, small_glow_surface

    # check if the bullets image and glow is still on the screen_flags
    # otherwise set it to dead
    def check_dead(self):
        if self.rect.center[0] + self.big_glow_size < 0:
            self.dead = True
        elif self.rect.center[0] - self.big_glow_size > 512:
            self.dead = True
        elif self.rect.center[1] + self.big_glow_size < 0:
            self.dead = True
        elif self.rect.center[1] - self.big_glow_size > 288:
            self.dead = True

    # draws the shooting animation
    def draw_sparkle(self, surface):
        # raise the count and change the frame
        self.frame_count += 1 * self.dt
        if self.frame_count / 60 >= self.frame_change:
            self.frame_count = 0
            self.frame += 1

            # if we reached the end of the animation
            # save that and return
            if self.frame == self.sparkle_frames_length - 1:
                self.sparkle_done = True
                return

            # otherwise grab the image
            self.sparkle_image = self.sparkle_frames[self.frame]

        # and draw the image ont the screen
        surface.blit(self.sparkle_image, (self.render_x, self.render_y))

    # updates the particles for the bullets particle trail
    def update_particles(self, surface):
        # spawn particle if its time to do so
        self.move_particle_count += 1 * self.dt
        if self.move_particle_count >= self.move_particle_time:
            self.move_particle_count = 0

            # set the particles attributes
            center = list(funcs.render_pos_to_screen_pos(self.rect.center, (1920, 1080)))
            velocity = [randint(1, 20) / 10 - 1, randint(1, 20) / 10 - 1]
            radius = randint(1, 3)
            lifetime = 2

            # create a particle object and add it to the list
            p = particle.Particle(center, velocity, radius, lifetime, self.move_particle_color, self.move_particle_glow_color, has_glow=True)
            self.particles.append(p)

        # update all particles in the list
        # check if their alive and if so update them otherwise...
        to_remove = []
        for entity in self.particles:
            if entity.dead:
                to_remove.append(entity)
            else:
                entity.update(surface)

        # ...remove them from the list
        for entity in to_remove:
            self.particles.remove(entity)

