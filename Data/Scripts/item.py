import pygame
from random import randint
import time


from . import particle
from . import funcs


# this object represents a gold coin or a mana orb
class Item:
    # set the attributes
    def __init__(self, name, center, velocity, landed_rocks, falling_rocks):
        # the name it the type of item
        self.name = name

        self.center = center
        self.velocity = velocity
        self.gravity = 0.2

        # lists with all the rocks for collision detection
        self.landed_rocks = landed_rocks
        self.falling_rocks = falling_rocks

        # variables to change the frames of the animation
        self.frames_count = 0
        self.frames_change = 5
        self.frame = randint(0, 5)

        # state of the item
        self.collected = False
        self.collectable = False

        # count for the collectable delay after being spawned
        self.collectable_delay = 20
        self.collectable_delay_count = 0

        self.particles = []

        # variables for spawning particles
        self.move_particle_time = 10
        self.move_particle_count = 0

        # these two rects represent the left and right map border
        self.left_border_rect = pygame.rect.Rect(0, 0, 16, 288)
        self.right_border_rect = pygame.rect.Rect(512 - 16, 0, 16, 288)

        # set parameters for the animation and particle color based on the type of the item
        if self.name == 'mana':
            self.frames_len = 15
            path = 'Data/Assets/Sprites/Items/Mana/mana_'
            self.move_particle_color = (129, 212, 250)
            self.move_particle_glow_color = (0, 8, 11)
        elif self.name == 'gold':
            self.frames_len = 15
            path = 'Data/Assets/Sprites/Items/Gold/gold_'
            self.move_particle_color = (224, 192, 95)
            self.move_particle_glow_color = (14, 10, 0)

        # load the animation frames into a list
        self.frames = []
        for i in range(self.frames_len):
            image = pygame.image.load(path + f'{i + 1}.png').convert_alpha()
            self.frames.append(image)

        # set the image to the first frame and set the hit box and the mask for pixel perfect collision
        self.image = self.frames[self.frame]
        self.rect = self.image.get_rect()
        self.rect.center = self.center
        self.mask = pygame.mask.from_surface(self.image)

        # track time between frames
        self.dt = 0
        self.last_time = time.time()

        # load the crush sound and set its volume
        self.crush_sound = pygame.mixer.Sound('Data/Assets/Sound/Sfx/item_crush_1.wav')
        self.crush_sound.set_volume(.1)

    # main update function
    def update(self, surface, paused):
        # calculate delta time since the last frame
        self.dt = time.time() - self.last_time
        self.dt *= 60
        self.last_time = time.time()

        # get the current image
        self.get_image()

        if not paused:
            # check if the item is collectable
            if not self.collectable:
                self.check_collectable()

            # move left right, set the hit box and check collision
            self.center[0] += self.velocity[0] * self.dt
            self.rect.centerx = self.center[0]
            self.check_collision_x()

            # move up down, set the hit box and check collision
            self.center[1] += self.velocity[1] * self.dt
            self.rect.centery = self.center[1]
            self.check_collision_y()

            # apply gravity to the vertical movement
            self.apply_gravity()

        # draw the image to the surface
        surface.blit(self.image, self.rect)

    # checks the collision on the x-axis
    def check_collision_x(self):
        # get all the landed rocks the item collides with
        landed_rock_hit_list = pygame.sprite.spritecollide(self, self.landed_rocks, False)

        # if there is at least one we undo the movement from the update function, set the hit box and change the movement direction + slow the movement down
        if len(landed_rock_hit_list) > 0:
            self.center[0] -= self.velocity[0] * self.dt
            self.rect.centerx = self.center[0]
            self.velocity[0] *= -.75

        # do the same thing for the falling rocks...
        falling_rock_hit_list = pygame.sprite.spritecollide(self, self.falling_rocks, False)
        if len(falling_rock_hit_list) > 0:
            if self.velocity[0] != 0:
                self.center[0] -= self.velocity[0] * self.dt
                self.rect.centerx = self.center[0]
            self.velocity[0] *= -.75

        # ...and the same thing for the left map border...
        if self.rect.colliderect(self.left_border_rect):
            self.rect.left = self.left_border_rect.right
            self.center = list(self.rect.center)
            self.velocity[0] *= -.75

        # ...and the right map border
        if self.rect.colliderect(self.right_border_rect):
            self.rect.right = self.right_border_rect.left
            self.center = list(self.rect.center)
            self.velocity[0] *= -.75

    # checks for collision on the y-axis
    def check_collision_y(self):
        # check for collision with landed rocks
        landed_rock_hit_list = pygame.sprite.spritecollide(self, self.landed_rocks, False)

        # if there is at least one we undo the movement from the update function, set the hit box and change the movement direction + slow the movement down
        if len(landed_rock_hit_list) > 0:
            if self.velocity[1] != 0:
                self.center[1] -= self.velocity[1] * self.dt
                self.rect.centery = self.center[1]
            self.velocity[1] *= -.25

        # for the falling rocks, do basically the same thing but...
        falling_rock_hit_list = pygame.sprite.spritecollide(self, self.falling_rocks, False)
        for entity in falling_rock_hit_list:
            # ...if the item is under the rock it gets destroyed
            if self.rect.y >= entity.rect.y:
                self.collected = True
                self.crush_sound.play()
            # otherwise it bounces away
            else:
                self.center[1] -= self.velocity[1] * self.dt
                self.rect.centery = self.center[1]
                self.velocity[1] *= -.25

    # this function adds the gravity to the movement speed on the y-axis
    def apply_gravity(self):
        self.velocity[1] += self.gravity * self.dt

    # this function counts the time since the item is being spawned
    def check_collectable(self):
        self.collectable_delay_count += 1 * self.dt

        # and makes it collectable to the player
        if self.collectable_delay_count >= self.collectable_delay:
            self.collectable = True

    # this function is being called by the player on collision
    def collect(self):
        self.collected = True

    # get the current image from the animation
    def get_image(self):
        # count the time since the last frame and update the frame number
        self.frames_count += 1 * self.dt
        if self.frames_count >= self.frames_change:
            self.frames_count = 0
            self.frame += 1

            # and reset the frame number at the and of the animation
            if self.frame > self.frames_len - 1:
                self.frame = 0

            # get the new image from the animation list and update the mask for the pixel perfect animation
            self.image = self.frames[self.frame]
            self.mask = pygame.mask.from_surface(self.image)

    # this function updates and spawns the particles
    def update_particles(self, surface, paused, dead, no_particle_rect):
        # spawn particle if its the time to do so
        self.move_particle_count += 1 * self.dt
        if self.move_particle_count >= self.move_particle_time:
            self.move_particle_count = 0

            # set the particles attributes
            center = list(funcs.render_pos_to_screen_pos(self.rect.center, (1920, 1080)))
            velocity = [randint(1, 10) / 10 - .5, randint(1, 10) / 10 - .5]
            radius = randint(1, 3)
            lifetime = 1

            # create a new particle object and add it to the list
            p = particle.Particle(center, velocity, radius, lifetime, self.move_particle_color, self.move_particle_glow_color, has_glow=True)
            self.particles.append(p)

        # update the particles and remove them if they are dead
        to_remove = []
        for entity in self.particles:
            if entity.dead:
                to_remove.append(entity)
            else:
                # do not draw the particle onto a hud message
                if paused or dead:
                    entity.update(surface, no_particle_rect)
                else:
                    entity.update(surface)

        for entity in to_remove:
            self.particles.remove(entity)


