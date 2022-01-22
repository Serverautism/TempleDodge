import pygame
from random import randint
import time
import math


from . import item
from . import particle
from . import funcs


# this object represents one of the treasure chests
class Chest:
    # first set the attributes
    def __init__(self, rock, name, landed_rocks, falling_rocks):
        # the rock if the object the chest is 'placed on' and the name is the item inside
        self.rock = rock
        self.name = name

        # lists with all of the rocks for collision detection
        self.landed_rocks = landed_rocks
        self.falling_rocks = falling_rocks

        # load the images and set the hit box + position based on the rock the chest is standing on
        self.closed_image = pygame.image.load(f'Data/Assets/Sprites/Chest/chest_{self.name}_1.png').convert_alpha()
        self.open_image = pygame.image.load(f'Data/Assets/sprites/Chest/chest_{self.name}_2.png').convert_alpha()
        self.rect = self.closed_image.get_rect()
        self.rect.bottom = self.rock.rect.top

        if self.rock.width == 1:
            self.rect.x = self.rock.rect.x
        elif self.rock.width == 2:
            self.rect.centerx = self.rock.rect.centerx

        # tracker for the current state of the chest
        self.opened = False
        self.crushed = False
        self.done = False

        self.particles = []
        self.items = []

        # set a few parameters for spawning particles and items based on the item the chest is holding
        if self.name == 'gold':
            self.drop_count = 5
            self.death_particle_color = (110, 97, 0)
            self.death_particle_glow_color = (5, 4, 0)
            self.open_particle_color = (120, 107, 10)
            self.open_particle_glow_color = (5, 4, 0)
        elif self.name == 'mana':
            self.drop_count = 1
            self.death_particle_color = (0, 74, 112)
            self.death_particle_glow_color = (0, 4, 6)
            self.open_particle_color = (10, 84, 122)
            self.open_particle_glow_color = (0, 4, 6)

        # track the time between two frames
        self.dt = 0
        self.last_time = time.time()

        self.particles = []

        # how many particles should be spawned
        self.open_particle_amuont = 60
        self.death_particle_amuont = 60

        # load the sounds and set their volume
        self.crush_sound = pygame.mixer.Sound('Data/Assets/Sound/Sfx/chest_crush_1.wav')
        self.crush_sound.set_volume(.1)
        self.open_sound = pygame.mixer.Sound('Data/Assets/Sound/Sfx/chest_open_1.wav')
        self.open_sound.set_volume(.1)

    # main update function
    def update(self, surface):
        # if the chest did not got hit by a rock
        if not self.crushed:
            # determine delta time
            self.dt = time.time() - self.last_time
            self.dt *= 60
            self.last_time = time.time()

            # move to the rock
            self.rect.bottom = self.rock.rect.top

            # check if it collides with a rock and if so the chest gets crushed
            for entity in self.falling_rocks:
                if self.rect.colliderect(entity.rect):
                    self.crush()

            # draw the closed or opened images based on
            # if the player opened the chest
            if self.opened:
                surface.blit(self.open_image, self.rect)
            else:
                surface.blit(self.closed_image, self.rect)

        # if the chest did get crushed we just check if there are particles alive
        # otherwise set the chest to done
        else:
            if len(self.particles) <= 0:
                self.done = True

        # if the chest if off screen set it to done as well
        if self.rect.y >= 288:
            self.done = True

    # function gets called whenever the player collides with the chest
    def open(self):
        # if the chest can be open_sound
        # track it, play a sound spawn particles and spawn the items
        if not self.opened and not self.crushed:
            self.opened = True
            self.open_sound.play()
            self.add_open_particles()

            for i in range(self.drop_count):
                velocity = [randint(0, 40)/10 - 2, -1]
                self.items.append(item.Item(self.name, [self.rect.center[0], self.rect.top], velocity, self.landed_rocks, self.falling_rocks))

    # gets called when the chest gets hit by a rock
    def crush(self):
        # track it play a sound and spawn particles based on if the chest is holding an item or not
        self.crushed = True
        self.crush_sound.play()

        if not self.opened:
            self.add_death_particles(5)
        else:
            self.add_death_particles(2)

    # adds the circle particle animation
    def add_death_particles(self, speed):
        for i in range(self.death_particle_amuont):
            center = list(funcs.render_pos_to_screen_pos(self.rect.center, (1920, 1080)))

            # split 360 degrees by the number of particles
            radians = math.radians((360 / self.death_particle_amuont) * i)

            # set the velocity vector based on the angle the particle in flying at and add a little randomisation
            velocity = [speed * math.cos(radians) + (randint(1, 10) / 10 - .5), speed * math.sin(radians) + (randint(1, 10) / 10 - .5)]

            radius = randint(1, 5)
            lifetime = 2

            # create a particle object and add it to the list
            p = particle.Particle(center, velocity, radius, lifetime, self.death_particle_color, self.death_particle_glow_color, has_glow=True, gravity=.4)
            self.particles.append(p)

    # creates the particle fountain animation
    def add_open_particles(self):
        for i in range(self.open_particle_amuont):
            # the particles just fly up and a random amount to the left or right
            center = list(funcs.render_pos_to_screen_pos(self.rect.center, (1920, 1080)))
            velocity = [randint(1, 40) / 10 - 2, -8 + (randint(1, 20) / 10 - 1)]
            radius = randint(1, 5)
            lifetime = 1.5

            # create a particle object and add it to the list
            p = particle.Particle(center, velocity, radius, lifetime, self.open_particle_color, self.open_particle_glow_color, has_glow=True, gravity=.5)
            self.particles.append(p)

    # update particle function
    def update_particles(self, surface):
        # remove particles if they are dead or update them
        to_remove = []
        for entity in self.particles:
            if entity.dead:
                to_remove.append(entity)
            else:
                entity.update(surface)

        for entity in to_remove:
            self.particles.remove(entity)
