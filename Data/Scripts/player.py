import pygame
from random import randint
import time


from . import particle
from . import funcs


def load_frames(path, length):
    left = []
    right = []

    for i in range(length):
        image = pygame.image.load(path + f'{i + 1}.png').convert_alpha()
        right.append(image)
        left.append(pygame.transform.flip(image, True, False))

    return left, right


class MapBorder:
    def __init__(self):
        self.image = pygame.image.load('Data/Assets/Sprites/Map/walls.png').convert_alpha()
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)


class Player:
    def __init__(self, render_pos, landed_rocks, falling_rocks, chests, items, bullets):
        self.pos = list(render_pos)
        self.x, self.y = render_pos
        self.direction = 'R'
        self.state = 'idle'
        self.max_jumps = 5
        self.jump_count = self.max_jumps
        self.speed = 1
        self.jump_vel = 5
        self.dx = 0
        self.dy = 0
        self.gravity = 0.2
        self.jump_spin_degrees = 25
        self.jump_spin_done = False
        self.jump_rotation = 0
        self.rotations_per_jump = 3

        self.is_ghost = False
        self.ghost_speed = 2
        self.ghost_duration_time = 10
        self.ghost_count = 0
        self.godmode = False
        self.dead = False

        self.left_border_rect = pygame.rect.Rect(0, 0, 16, 288)
        self.right_border_rect = pygame.rect.Rect(512 - 16, 0, 16, 288)
        self.map_border = MapBorder()

        self.idle_frames_length = 4
        self.jump_frames_length = 1
        self.run_frames_length = 4
        self.ghost_frames_length = 1

        self.frame = 0
        self.frame_change = 0.1
        self.frame_count = 0

        self.last_time = time.time()
        self.dt = 1

        self.idle_frames_left, self.idle_frames_right = load_frames('Data/Assets/Sprites/Player/Idle/player_idle_', self.idle_frames_length)
        self.jump_frames_left, self.jump_frames_right = load_frames('Data/Assets/Sprites/Player/Jump/player_jump_', self.jump_frames_length)
        self.run_frames_left, self.run_frames_right = load_frames('Data/Assets/Sprites/Player/Run/player_run_', self.run_frames_length)
        self.ghost_frames_left, self.ghost_frames_right = load_frames('Data/Assets/Sprites/Player/Ghost/player_ghost_', self.ghost_frames_length)

        self.image = self.idle_frames_right[0]
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y

        self.falling_rocks = falling_rocks
        self.landed_rocks = landed_rocks
        self.chests = chests
        self.items = items
        self.bullets = bullets

        self.glow_color = (0, 8, 11)
        self.ghost_rect_width = self.ghost_frames_left[0].get_width()
        self.big_glow_size = self.ghost_rect_width * 2
        self.small_glow_size = self.ghost_rect_width
        self.glow_grow = True

        self.gold_count = 0
        self.mana_count = 0
        self.max_mana = 7

        self.particles = []

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

        self.jump_sound = pygame.mixer.Sound('Data/Assets/Sound/Sfx/jump_1.wav')
        self.jump_sound.set_volume(.1)

        self.hit_sound = pygame.mixer.Sound('Data/Assets/Sound/Sfx/hit_1.wav')
        self.hit_sound.set_volume(.1)

        self.pickup_coin_sound = pygame.mixer.Sound('Data/Assets/Sound/Sfx/pickup_coin_1.wav')
        self.pickup_coin_sound.set_volume(.1)

        self.pickup_mana_sound = pygame.mixer.Sound('Data/Assets/Sound/Sfx/pickup_mana_1.wav')
        self.pickup_mana_sound.set_volume(.1)

    def update(self, surface, paused):
        if not self.dead:
            # determine delta time
            self.dt = time.time() - self.last_time
            self.dt *= 60
            self.last_time = time.time()
            if not paused:
                # move x, check collision
                self.x += self.dx * self.dt
                self.rect.x = self.x
                self.check_collision_x()

                # move y, check collision
                if not self.is_ghost:
                    self.calc_grav()
                self.y += self.dy * self.dt
                self.rect.y = self.y
                self.check_collision_y()

                # check bullets
                self.check_bullets()

                # check chests and items
                self.check_chests()
                self.check_items()

                # update ghost state
                if self.is_ghost:
                    self.check_ghost_state()
                    glow_big, glow_small = self.get_glow()

                    surface.blit(glow_big, (self.rect.center[0] - self.big_glow_size, self.rect.center[1] - self.big_glow_size), special_flags=pygame.BLEND_RGB_ADD)
                    surface.blit(glow_small, (self.rect.center[0] - self.small_glow_size, self.rect.center[1] - self.small_glow_size), special_flags=pygame.BLEND_RGB_ADD)

                # get image and draw
                self.get_image()
            surface.blit(self.image, self.rect)

    def calc_grav(self):
        # Calculate effect of gravity
        if self.dy == 0:
            self.dy = 1
        else:
            self.dy += self.gravity * self.dt

    def check_collision_x(self):
        landed_rock_hit_list = pygame.sprite.spritecollide(self, self.landed_rocks, False, pygame.sprite.collide_mask)
        if len(landed_rock_hit_list) > 0:
            self.collide_x()

        falling_rock_hit_list = pygame.sprite.spritecollide(self, self.falling_rocks, False, pygame.sprite.collide_mask)
        if len(falling_rock_hit_list) > 0:
            self.collide_x()

        border_collision = pygame.sprite.spritecollide(self, [self.map_border], False, pygame.sprite.collide_mask)
        if border_collision:
            self.collide_x()

    def check_collision_y(self):
        landed_rock_hit_list = pygame.sprite.spritecollide(self, self.landed_rocks, False, pygame.sprite.collide_mask)
        for entity in landed_rock_hit_list:
            # check if dy > 0?
            self.rect.bottom = entity.rect.top
            self.y = self.rect.top
            self.dy = 0
            self.jump_count = self.max_jumps
            if self.dx != 0:
                self.state = 'run'
            else:
                self.state = 'idle'

        falling_rock_hit_list = pygame.sprite.spritecollide(self, self.falling_rocks, False, pygame.sprite.collide_mask)
        for entity in falling_rock_hit_list:
            if self.rect.y >= entity.rect.y:
                self.hit()
            else:
                self.rect.bottom = entity.rect.top
                self.y = self.rect.top
                self.dy = 0
                self.jump_count = self.max_jumps
                if self.dx != 0:
                    self.state = 'run'
                else:
                    self.state = 'idle'

    def collide_x(self):
        if self.dx > 0:
            if not self.is_ghost:
                self.x -= self.speed * self.dt
                self.rect.x = self.x
            else:
                self.x -= self.ghost_speed * self.dt
                self.rect.x = self.x
        elif self.dx < 0:
            if not self.is_ghost:
                self.x += self.speed * self.dt
                self.rect.x = self.x
            else:
                self.x += self.ghost_speed * self.dt
                self.rect.x = self.x

    def check_bullets(self):
        bullet_hit_list = pygame.sprite.spritecollide(self, self.bullets, False, pygame.sprite.collide_mask)
        if len(bullet_hit_list) > 0:
            self.hit()

    def check_chests(self):
        for chest in self.chests:
            if self.rect.colliderect(chest.rect):
                chest.open()

    def check_items(self):
        item_hit_list = pygame.sprite.spritecollide(self, self.items, False, pygame.sprite.collide_mask)
        for entity in item_hit_list:
            if entity.collectable:
                entity.collect()
                if entity.name == 'gold':
                    self.gold_count += 1
                    self.pickup_coin_sound.play()
                elif entity.name == 'mana':
                    if self.mana_count < self.max_mana:
                        self.mana_count += 1
                    self.pickup_mana_sound.play()

    def check_ghost_state(self):
        self.ghost_count += 1 * self.dt
        if self.ghost_count / 60 >= self.ghost_duration_time:
            self.is_ghost = False
            self.ghost_count = 0
            self.frame = 0

    def go_left(self):
        if not self.is_ghost:
            self.dx = -self.speed
            self.direction = 'L'
            if self.state != 'jump':
                self.state = 'run'
        else:
            self.dx = -self.ghost_speed
            self.direction = 'L'

    def go_right(self):
        if not self.is_ghost:
            self.dx = self.speed
            self.direction = 'R'
            if self.state != 'jump':
                self.state = 'run'
        else:
            self.dx = self.ghost_speed
            self.direction = 'R'

    def go_up(self):
        if self.is_ghost:
            self.dy = -self.ghost_speed

    def go_down(self):
        if not self.is_ghost:
            if self.state == 'jump':
                self.dy = self.jump_vel
        else:
            self.dy = self.ghost_speed

    def enable_ghost_mode(self):
        if self.mana_count == self.max_mana:
            self.is_ghost = True
            self.mana_count = 0
            self.dy = 0

    def stop(self):
        self.dx = 0
        if self.state != 'jump':
            self.state = 'idle'

    def stop_ghost_y(self):
        if self.is_ghost:
            self.dy = 0

    def jump(self):
        if not self.is_ghost:
            if self.jump_count == 0:
                # check if player is on the ground
                self.rect.y += 2
                landed_rock_hit_list = pygame.sprite.spritecollide(self, self.landed_rocks, False, pygame.sprite.collide_mask)
                falling_rock_hit_list = pygame.sprite.spritecollide(self, self.falling_rocks, False, pygame.sprite.collide_mask)
                self.rect.y -= 2

                if len(landed_rock_hit_list) > 0 or len(falling_rock_hit_list) > 0:
                    self.jump_count = self.max_jumps
                    self.jump_count -= 1
                    self.dy = -self.jump_vel
                    self.state = 'jump'
                    self.jump_rotation = 0
                    self.jump_spin_done = False
                    self.add_jump_particles()
                    self.jump_sound.play()
            else:
                self.jump_count -= 1
                self.dy = -self.jump_vel
                self.state = 'jump'
                self.jump_rotation = 0
                self.jump_spin_done = False
                self.add_jump_particles()
                self.jump_sound.play()

    def hit(self):
        if not self.godmode:
            self.dead = True
            self.hit_sound.play()
            self.add_death_particles()

    def get_image(self):
        before_rect = self.rect.copy()

        self.frame_count += 1
        if self.frame_count / 60 >= self.frame_change / self.dt:
            self.frame += 1
            self.frame_count = 0

        # if player is not ghost
        if not self.is_ghost:
            # running
            if self.state == 'run':
                if self.frame > self.run_frames_length - 1:
                    self.frame = 0

                if self.direction == 'L':
                    self.image = self.run_frames_left[self.frame]
                else:
                    self.image = self.run_frames_right[self.frame]
            # jumping
            elif self.state == 'jump':
                if self.frame > self.jump_frames_length - 1:
                    self.frame = 0

                if not self.jump_spin_done:
                    self.jump_rotation += self.jump_spin_degrees * self.dt
                    if self.jump_rotation >= 360 * self.rotations_per_jump:
                        self.jump_rotation = 0
                        self.jump_spin_done = True

                if self.direction == 'L':
                    self.image = pygame.transform.rotate(self.jump_frames_left[self.frame], self.jump_rotation)
                else:
                    self.image = pygame.transform.rotate(self.jump_frames_right[self.frame], -self.jump_rotation)
            # idle
            elif self.state == 'idle':
                if self.frame > self.idle_frames_length - 1:
                    self.frame = 0

                if self.direction == 'L':
                    self.image = self.idle_frames_left[self.frame]
                else:
                    self.image = self.idle_frames_right[self.frame]

        # if player is ghost
        else:
            if self.frame > self.ghost_frames_length - 1:
                self.frame = 0

            if self.direction == 'L':
                self.image = self.ghost_frames_left[self.frame]
            else:
                self.image = self.ghost_frames_right[self.frame]

        self.rect = self.image.get_rect()
        self.rect.center = before_rect.center
        self.mask = pygame.mask.from_surface(self.image)

    def get_glow(self):
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

        big_glow_surface = pygame.Surface((self.big_glow_size * 2, self.big_glow_size * 2))
        big_glow_surface.set_colorkey((0, 0, 0))
        small_glow_surface = pygame.Surface((self.small_glow_size * 2, self.small_glow_size * 2))
        small_glow_surface.set_colorkey((0, 0, 0))

        pygame.draw.circle(big_glow_surface, self.glow_color, (self.big_glow_size, self.big_glow_size), self.big_glow_size)
        pygame.draw.circle(small_glow_surface, self.glow_color, (self.small_glow_size, self.small_glow_size), self.small_glow_size)

        return big_glow_surface, small_glow_surface

    def add_jump_particles(self):
        for i in range(self.jump_particle_ammount):
            center = list(funcs.render_pos_to_screen_pos([self.rect.x + (self.rect.width / self.jump_particle_ammount) * i, self.rect.bottom], (1920, 1080)))
            velocity = [randint(1, 10) / 10 - .5, randint(1, 10) / 10 - .5]
            radius = randint(1, 3)
            lifetime = 1

            p = particle.Particle(center, velocity, radius, lifetime, self.jump_particle_color, self.jump_particle_glow_color)
            self.particles.append(p)

    def add_death_particles(self):
        for i in range(self.death_particle_ammount):
            center = list(funcs.render_pos_to_screen_pos([self.rect.x + (self.rect.width / self.death_particle_ammount) * i, self.rect.bottom], (1920, 1080)))
            velocity = [randint(1, 40) / 10 - 2, randint(1, 80) / -10]
            radius = randint(1, 3)
            lifetime = 2

            p = particle.Particle(center, velocity, radius, lifetime, self.death_particle_color, self.death_particle_glow_color, has_glow=True, gravity=.5)
            self.particles.append(p)

    def update_particles(self, surface):
        # spawn particle
        if self.dx != 0 or self.dy != 0:
            self.move_particle_count += 1 * self.dt
            if self.move_particle_count >= self.move_particle_time:
                self.move_particle_count = 0

                center = list(funcs.render_pos_to_screen_pos(self.rect.center, (1920, 1080)))
                velocity = [randint(1, 10) / 10 - .5, randint(1, 10) / 10 - .5]
                radius = randint(1, 3)
                lifetime = 3

                p = particle.Particle(center, velocity, radius, lifetime, self.move_particle_color, self.move_particle_glow_color, has_glow=True)
                self.particles.append(p)

        # update_particles
        to_remove = []
        for entity in self.particles:
            if entity.dead:
                to_remove.append(entity)
            else:
                entity.update(surface)

        for entity in to_remove:
            self.particles.remove(entity)

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
