import pygame
from random import randint
import time


from . import particle
from . import funcs


# function used to load the player animations
def load_frames(path, length):
    left = []
    right = []

    for i in range(length):
        # load the images and store them in a list while flipping them vertically for the left direction
        image = pygame.image.load(path + f'{i + 1}.png').convert_alpha()
        right.append(image)
        left.append(pygame.transform.flip(image, True, False))

    return left, right


# this class is used for the collision with the left and right map border
# it imitates an Sprite object
class MapBorder:
    def __init__(self):
        self.image = pygame.image.load('Data/Assets/Sprites/Map/walls.png').convert_alpha()
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)


# this object represents the player
class Player:
    # first set the attributes
    def __init__(self, render_pos, landed_rocks, falling_rocks, chests, items, bullets):
        self.pos = list(render_pos)
        self.x, self.y = render_pos
        self.direction = 'R'

        # state is the animation that needs to be played
        self.state = 'idle'

        # how many time the player can jump without touching the ground
        self.max_jumps = 5

        self.jump_count = self.max_jumps
        self.speed = 1
        self.jump_vel = 5

        # delta x and delta y ist the distance the player moves per frame on each axis
        self.dx = 0
        self.dy = 0

        self.gravity = 0.2

        # how far and how often the player spins while jumping
        self.jump_spin_degrees = 25
        self.jump_spin_done = False
        self.jump_rotation = 0
        self.rotations_per_jump = 3

        # variables for the players 'ghost mode'
        self.is_ghost = False
        self.ghost_speed = 2
        self.ghost_duration_time = 10
        self.ghost_count = 0

        # god mode prevents the player from dying
        self.godmode = False
        self.dead = False

        # create a map border object for the collision
        self.map_border = MapBorder()

        # how many frames each animation has
        self.idle_frames_length = 4
        self.jump_frames_length = 1
        self.run_frames_length = 4
        self.ghost_frames_length = 1

        # keep track of the current frame
        self.frame = 0
        self.frame_change = 0.1
        self.frame_count = 0

        # track the time between two frames
        self.last_time = time.time()
        self.dt = 1

        # load the animations as lists of images
        self.idle_frames_left, self.idle_frames_right = load_frames('Data/Assets/Sprites/Player/Idle/player_idle_', self.idle_frames_length)
        self.jump_frames_left, self.jump_frames_right = load_frames('Data/Assets/Sprites/Player/Jump/player_jump_', self.jump_frames_length)
        self.run_frames_left, self.run_frames_right = load_frames('Data/Assets/Sprites/Player/Run/player_run_', self.run_frames_length)
        self.ghost_frames_left, self.ghost_frames_right = load_frames('Data/Assets/Sprites/Player/Ghost/player_ghost_', self.ghost_frames_length)

        # set the first image and create rect and mask for the collision and set the position
        self.image = self.idle_frames_right[0]
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y

        # list of all the objects to test for collision
        self.falling_rocks = falling_rocks
        self.landed_rocks = landed_rocks
        self.chests = chests
        self.items = items
        self.bullets = bullets

        # variables for the player ghost while he is in 'ghost mode'
        self.glow_color = (0, 8, 11)
        self.ghost_rect_width = self.ghost_frames_left[0].get_width()
        self.big_glow_size = self.ghost_rect_width * 2
        self.small_glow_size = self.ghost_rect_width
        self.glow_grow = True

        # counts for the items
        self.gold_count = 0
        self.mana_count = 7
        self.max_mana = 7

        self.particles = []

        # variables for spawning particles
        self.death_particle_ammount = 60
        self.death_particle_color = (255, 67, 58)
        self.death_particle_glow_color = (12, 1, 0)

        self.jump_particle_ammount = 20
        self.jump_particle_color = (224, 192, 95)
        self.jump_particle_glow_color = (14, 11, 0)

        self.move_particle_time = 4
        self.move_particle_count = 0
        self.move_particle_color = (206, 206, 206)
        self.move_particle_glow_color = (5, 5, 5)

        # load all sounds and set the volumes
        self.jump_sound = pygame.mixer.Sound('Data/Assets/Sound/Sfx/jump_1.wav')
        self.jump_sound.set_volume(.1)

        self.hit_sound = pygame.mixer.Sound('Data/Assets/Sound/Sfx/hit_1.wav')
        self.hit_sound.set_volume(.1)

        self.pickup_coin_sound = pygame.mixer.Sound('Data/Assets/Sound/Sfx/pickup_coin_1.wav')
        self.pickup_coin_sound.set_volume(.1)

        self.pickup_mana_sound = pygame.mixer.Sound('Data/Assets/Sound/Sfx/pickup_mana_1.wav')
        self.pickup_mana_sound.set_volume(.1)

    # main update function
    def update(self, surface, paused):
        if not self.dead:
            # determine delta time since the last frame
            self.dt = time.time() - self.last_time
            self.dt *= 60
            self.last_time = time.time()

            if not paused:
                # move on x-axis and check for collision
                self.x += self.dx * self.dt
                self.rect.x = self.x
                self.check_collision_x()

                # apply gravity + move on y-axis and check for collision
                if not self.is_ghost:
                    self.calc_grav()
                self.y += self.dy * self.dt
                self.rect.y = self.y
                self.check_collision_y()

                # check collision with bullets
                self.check_bullets()

                # check collision with chests and items
                self.check_chests()
                self.check_items()

                # update the 'ghost state'
                if self.is_ghost:
                    # check if the 'ghost mode' is still valid
                    self.check_ghost_state()

                    # get the surfaces holding the images of the glow
                    glow_big, glow_small = self.get_glow()

                    # draw the glow
                    surface.blit(glow_big, (self.rect.center[0] - self.big_glow_size, self.rect.center[1] - self.big_glow_size), special_flags=pygame.BLEND_RGB_ADD)
                    surface.blit(glow_small, (self.rect.center[0] - self.small_glow_size, self.rect.center[1] - self.small_glow_size), special_flags=pygame.BLEND_RGB_ADD)

                # get the current image and draw it
                self.get_image()
            surface.blit(self.image, self.rect)

    # apply the gravity force to the player
    def calc_grav(self):
        # if he is on the ground set it to 1
        if self.dy == 0:
            self.dy = 1
        # otherwise raise the gravity velocity
        else:
            self.dy += self.gravity * self.dt

    # checks the collision on the x-axis with the rocks and the map border
    def check_collision_x(self):
        # list of all landed rocks the player collides with
        landed_rock_hit_list = pygame.sprite.spritecollide(self, self.landed_rocks, False, pygame.sprite.collide_mask)

        # if there is at least one we handle the collision on the x-axis
        if len(landed_rock_hit_list) > 0:
            self.x -= self.dx * self.dt
            self.rect.x = self.x

        # same for the falling rocks
        falling_rock_hit_list = pygame.sprite.spritecollide(self, self.falling_rocks, False)
        if len(falling_rock_hit_list) > 0:
            self.x -= self.dx * self.dt
            self.rect.x = self.x

        # and the map borders
        border_collision = pygame.sprite.spritecollide(self, [self.map_border], False, pygame.sprite.collide_mask)
        if border_collision:
            self.x -= self.dx * self.dt
            self.rect.x = self.x

    # checks the collision on the y-axis
    def check_collision_y(self):
        # list of all landed rocks the player collides with
        landed_rock_hit_list = pygame.sprite.spritecollide(self, self.landed_rocks, False, pygame.sprite.collide_mask)

        # move the player on top of the rock
        for entity in landed_rock_hit_list:
            self.rect.bottom = entity.rect.top
            self.y = self.rect.top

            # stop the vertical movement
            self.dy = 0

            # reset the jumps the player can do
            self.jump_count = self.max_jumps

            # change the animation
            if self.dx != 0:
                self.state = 'run'
            else:
                self.state = 'idle'

        # basically the same for the falling rocks
        falling_rock_hit_list = pygame.sprite.spritecollide(self, self.falling_rocks, False, pygame.sprite.collide_mask)
        for entity in falling_rock_hit_list:
            # if the player is under the rock he gets hit
            if self.rect.y >= entity.rect.y:
                self.hit()

            # otherwise do the same we did for the landed rocks
            else:
                self.rect.bottom = entity.rect.top
                self.y = self.rect.top
                self.dy = 0
                self.jump_count = self.max_jumps
                if self.dx != 0:
                    self.state = 'run'
                else:
                    self.state = 'idle'

    # check the collision with the projectiles
    # if the player collides with one he he gets hit
    def check_bullets(self):
        bullet_hit_list = pygame.sprite.spritecollide(self, self.bullets, False, pygame.sprite.collide_mask)
        if len(bullet_hit_list) > 0:
            self.hit()

    # if the player collides with a chest the chest gets opened
    def check_chests(self):
        for chest in self.chests:
            if self.rect.colliderect(chest.rect):
                chest.open()

    # checks if the player collides with an item
    def check_items(self):
        item_hit_list = pygame.sprite.spritecollide(self, self.items, False, pygame.sprite.collide_mask)
        for entity in item_hit_list:
            if entity.collectable:
                # if he does and the item is collectable
                # we raise the counter and play the sound depending on the type of the item
                entity.collect()
                if entity.name == 'gold':
                    self.gold_count += 1
                    self.pickup_coin_sound.play()
                elif entity.name == 'mana':
                    # mana is capped at certain amount
                    if self.mana_count < self.max_mana:
                        self.mana_count += 1
                    self.pickup_mana_sound.play()

    # keeps track of the time the player is a 'ghost' and sets him back to normal if the time runs out
    def check_ghost_state(self):
        self.ghost_count += 1 * self.dt
        if self.ghost_count / 60 >= self.ghost_duration_time:
            self.is_ghost = False
            self.ghost_count = 0
            self.frame = 0

    # set the movement on the x-axis for left movement and change the animation if the player is not a 'ghost'
    def go_left(self):
        if not self.is_ghost:
            self.dx = -self.speed
            self.direction = 'L'
            if self.state != 'jump':
                self.state = 'run'
        else:
            self.dx = -self.ghost_speed
            self.direction = 'L'

    # set the movement on the x-axis for right movement and change the animation if the player is not a 'ghost'
    def go_right(self):
        if not self.is_ghost:
            self.dx = self.speed
            self.direction = 'R'
            if self.state != 'jump':
                self.state = 'run'
        else:
            self.dx = self.ghost_speed
            self.direction = 'R'

    # lets the player move up if he is a 'ghost'
    def go_up(self):
        if self.is_ghost:
            self.dy = -self.ghost_speed

    # lets the player go down if he is a 'ghost' otherwise it cancels a jump
    def go_down(self):
        if not self.is_ghost:
            if self.state == 'jump':
                self.dy = self.jump_vel
        else:
            self.dy = self.ghost_speed

    # sets the players to ghost mode at the cost of mana
    def enable_ghost_mode(self):
        if self.mana_count == self.max_mana:
            self.is_ghost = True
            self.mana_count = 0
            self.dy = 0

    # stops the players movement on the x-axis
    def stop(self):
        self.dx = 0
        if self.state != 'jump':
            self.state = 'idle'

    # stops the movement on the y-axis only if the player is a 'ghost'
    def stop_ghost_y(self):
        if self.is_ghost:
            self.dy = 0

    # lets the player jump if he is not a ghost
    def jump(self):
        if not self.is_ghost:
            # if the player has no jumps left
            if self.jump_count == 0:
                # check if player is on the ground by moving him down a bit...
                self.rect.y += 2
                # ...check for collision with rocks...
                landed_rock_hit_list = pygame.sprite.spritecollide(self, self.landed_rocks, False, pygame.sprite.collide_mask)
                falling_rock_hit_list = pygame.sprite.spritecollide(self, self.falling_rocks, False, pygame.sprite.collide_mask)
                # ...and move him back up
                self.rect.y -= 2

                # if there is a rock under him
                if len(landed_rock_hit_list) > 0 or len(falling_rock_hit_list) > 0:
                    # reset the amount of possible jumps
                    self.jump_count = self.max_jumps - 1

                    # give the player upwards movement and set his animation
                    self.dy = -self.jump_vel
                    self.state = 'jump'

                    # reset his rotation
                    self.jump_rotation = 0
                    self.jump_spin_done = False

                    # add particles and play the jump sound
                    self.add_jump_particles()
                    self.jump_sound.play()
            else:
                # if he has jumps left, just subtract one and let him jump list above
                self.jump_count -= 1
                self.dy = -self.jump_vel
                self.state = 'jump'
                self.jump_rotation = 0
                self.jump_spin_done = False
                self.add_jump_particles()
                self.jump_sound.play()

    # gets called whenever the player gets hit
    def hit(self):
        if not self.godmode:
            # if he is not in god mode he dies, we play the sound and add the death particles
            self.dead = True
            self.hit_sound.play()
            self.add_death_particles()

    # gets the players image for the animations
    def get_image(self):
        # do a copy of rect
        before_rect = self.rect.copy()

        # check if its time for the next frame
        self.frame_count += 1
        if self.frame_count / 60 >= self.frame_change / self.dt:
            self.frame += 1
            self.frame_count = 0

        # if player is not a 'ghost'
        if not self.is_ghost:
            # if he is running
            if self.state == 'run':
                # check if the frame is greater then the length of the animation
                if self.frame > self.run_frames_length - 1:
                    self.frame = 0

                # get the image from the list depending on the frame and the players direction
                if self.direction == 'L':
                    self.image = self.run_frames_left[self.frame]
                else:
                    self.image = self.run_frames_right[self.frame]

            # same for the players jump...
            elif self.state == 'jump':
                if self.frame > self.jump_frames_length - 1:
                    self.frame = 0

                # ...but we rotate the players image for a maximum of 3 rotation per jump
                if not self.jump_spin_done:
                    self.jump_rotation += self.jump_spin_degrees * self.dt
                    if self.jump_rotation >= 360 * self.rotations_per_jump:
                        self.jump_rotation = 0
                        self.jump_spin_done = True

                # then grab the image and rotate it
                if self.direction == 'L':
                    self.image = pygame.transform.rotate(self.jump_frames_left[self.frame], self.jump_rotation)
                else:
                    self.image = pygame.transform.rotate(self.jump_frames_right[self.frame], -self.jump_rotation)

            # same as we did for the run animation but for th idle animation
            elif self.state == 'idle':
                if self.frame > self.idle_frames_length - 1:
                    self.frame = 0

                if self.direction == 'L':
                    self.image = self.idle_frames_left[self.frame]
                else:
                    self.image = self.idle_frames_right[self.frame]

        # if player is in 'ghost' mode
        # we do the same but with the ghost animation
        else:
            if self.frame > self.ghost_frames_length - 1:
                self.frame = 0

            if self.direction == 'L':
                self.image = self.ghost_frames_left[self.frame]
            else:
                self.image = self.ghost_frames_right[self.frame]

        # then we grab the new rect and set the center to the center of the old rect
        self.rect = self.image.get_rect()
        self.rect.center = before_rect.center

        # then we get the new mask for the pixel perfect collision
        self.mask = pygame.mask.from_surface(self.image)

    # this function returns the surfaces with the glow
    def get_glow(self):
        # check if the glow if getting bigger or smaller for the pulsating effect
        # then change its size and check if it should get smaller or bigger next time
        if self.glow_grow:
            if self.big_glow_size >= self.ghost_rect_width * 3:
                self.glow_grow = False

            self.big_glow_size += 1
            self.small_glow_size += 1
        else:
            if self.big_glow_size <= self.ghost_rect_width * 2:
                self.glow_grow = True

            self.big_glow_size -= 1
            self.small_glow_size -= 1

        # create a new surface with the size of the glow for the big and small one
        big_glow_surface = pygame.Surface((self.big_glow_size * 2, self.big_glow_size * 2))
        big_glow_surface.set_colorkey((0, 0, 0))
        small_glow_surface = pygame.Surface((self.small_glow_size * 2, self.small_glow_size * 2))
        small_glow_surface.set_colorkey((0, 0, 0))

        # then draw the glows to the surface
        pygame.draw.circle(big_glow_surface, self.glow_color, (self.big_glow_size, self.big_glow_size), self.big_glow_size)
        pygame.draw.circle(small_glow_surface, self.glow_color, (self.small_glow_size, self.small_glow_size), self.small_glow_size)

        return big_glow_surface, small_glow_surface

    # adds the jump particle animation
    def add_jump_particles(self):
        for i in range(self.jump_particle_ammount):
            # set the particles attributes
            center = list(funcs.render_pos_to_screen_pos([self.rect.x + (self.rect.width / self.jump_particle_ammount) * i, self.rect.bottom], (1920, 1080)))
            velocity = [randint(1, 10) / 10 - .5, randint(1, 10) / 10 - .5]
            radius = randint(1, 3)
            lifetime = 1

            # create a new particle object and add it to the list
            p = particle.Particle(center, velocity, radius, lifetime, self.jump_particle_color, self.jump_particle_glow_color)
            self.particles.append(p)

    # do the same for the death particle animation
    def add_death_particles(self):
        for i in range(self.death_particle_ammount):
            center = list(funcs.render_pos_to_screen_pos([self.rect.x + (self.rect.width / self.death_particle_ammount) * i, self.rect.bottom], (1920, 1080)))
            velocity = [randint(1, 40) / 10 - 2, randint(1, 80) / -10]
            radius = randint(1, 3)
            lifetime = 2

            p = particle.Particle(center, velocity, radius, lifetime, self.death_particle_color, self.death_particle_glow_color, has_glow=True, gravity=.5)
            self.particles.append(p)

    # updates all of the particles and spawns the particles for the player particle trail
    def update_particles(self, surface):
        # spawn a particle if its time to do so
        if self.dx != 0 or self.dy != 0:
            self.move_particle_count += 1 * self.dt
            if self.move_particle_count >= self.move_particle_time:
                self.move_particle_count = 0

                # set the particles attributes
                center = list(funcs.render_pos_to_screen_pos(self.rect.center, (1920, 1080)))
                velocity = [randint(1, 10) / 10 - .5, randint(1, 10) / 10 - .5]
                radius = randint(1, 3)
                lifetime = 3

                # create a new particle object and add it to the list
                p = particle.Particle(center, velocity, radius, lifetime, self.move_particle_color, self.move_particle_glow_color, has_glow=True)
                self.particles.append(p)

        # update the particles and remove the particles if they are dead
        to_remove = []
        for entity in self.particles:
            if entity.dead:
                to_remove.append(entity)
            else:
                entity.update(surface)

        for entity in to_remove:
            self.particles.remove(entity)

    # reset the players attributes before starting a new round
    def reset(self, center):
        self.dead = False
        self.gold_count = 0
        self.mana_count = 0
        self.direction = 'R'
        self.state = 'idle'
        self.rect.center = center
        self.x = self.rect.x
        self.y = self.rect.y
        self.jump_count = self.max_jumps
        self.dx = 0
        self.dy = 0
        self.jump_spin_done = False
        self.jump_rotation = 0
        self.is_ghost = False
        self.ghost_count = 0
        self.frame = 0
        self.frame_count = 0
        self.last_time = time.time()
        self.dt = 1
        self.particles.clear()
