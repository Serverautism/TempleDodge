import pygame


class Player:
    def __init__(self, render_pos, landed_rocks=[], falling_rocks=[], chests=[], items=[], bullets=[]):
        self.pos = render_pos
        self.x, self.y = render_pos
        self.direction = 'R'
        self.state = 'idle'
        self.max_jumps = 2
        self.jump_count = self.max_jumps
        self.speed = 1
        self.jump_vel = 5
        self.dx = 0
        self.dy = 0
        self.gravity = 0.2

        self.idle_frames_length = 4
        self.jump_frames_length = 1
        self.run_frames_length = 4

        self.frame = 0
        self.frame_change = 0.1
        self.frame_count = 0

        self.idle_frames_left, self.idle_frames_right = self.load_frames('Data/Assets/Sprites/Player/Idle/player_idle_', self.idle_frames_length)
        self.jump_frames_left, self.jump_frames_right = self.load_frames('Data/Assets/Sprites/Player/Jump/player_jump_', self.jump_frames_length)
        self.run_frames_left, self.run_frames_right = self.load_frames('Data/Assets/Sprites/Player/Run/player_run_', self.run_frames_length)

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

    def update(self, surface):
        # move x, check collision
        self.rect.x += self.dx
        self.check_collision_x()

        # move y, check collision
        self.calc_grav()
        self.rect.y += self.dy
        self.check_collision_y()

        # get image and draw
        self.get_image()
        surface.blit(self.image, self.rect)

    def calc_grav(self):
        # Calculate effect of gravity
        if self.dy == 0:
            self.dy = 1
        else:
            self.dy += self.gravity

    def check_collision_x(self):
        landed_rock_hit_list = pygame.sprite.spritecollide(self, self.landed_rocks, False, pygame.sprite.collide_mask)
        if len(landed_rock_hit_list) > 0:
            if self.dx > 0:
                self.rect.x -= self.speed
            elif self.dx < 0:
                self.rect.x += self.speed

        falling_rock_hit_list = pygame.sprite.spritecollide(self, self.falling_rocks, False, pygame.sprite.collide_mask)
        if len(falling_rock_hit_list) > 0:
            if self.dx > 0:
                self.rect.x -= self.speed
            elif self.dx < 0:
                self.rect.x += self.speed

    def check_collision_y(self):
        landed_rock_hit_list = pygame.sprite.spritecollide(self, self.landed_rocks, False, pygame.sprite.collide_mask)
        for entity in landed_rock_hit_list:
            # check if dy > 0?
            self.rect.bottom = entity.rect.top
            self.dy = 0
            self.jump_count = self.max_jumps
            if self.dx != 0:
                self.state = 'run'
            else:
                self.state = 'idle'

        falling_rock_hit_list = pygame.sprite.spritecollide(self, self.falling_rocks, False, pygame.sprite.collide_mask)
        for entity in falling_rock_hit_list:
            if self.dy <= 0:
                print('dead')
            else:
                self.rect.bottom = entity.rect.top
                self.dy = 0
                self.jump_count = self.max_jumps
                if self.dx != 0:
                    self.state = 'run'
                else:
                    self.state = 'idle'

    def go_left(self):
        self.dx = -self.speed
        self.direction = 'L'
        if self.state != 'jump':
            self.state = 'run'

    def go_right(self):
        self.dx = self.speed
        self.direction = 'R'
        if self.state != 'jump':
            self.state = 'run'

    def stop(self):
        self.dx = 0
        if self.state != 'jump':
            self.state = 'idle'

    def jump(self):
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
        else:
            self.jump_count -= 1
            self.dy = -self.jump_vel
            self.state = 'jump'

    def get_image(self):
        self.frame_count += 1
        if self.frame_count / 60 >= self.frame_change:
            self.frame += 1
            self.frame_count = 0

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

            if self.direction == 'L':
                self.image = self.jump_frames_left[self.frame]
            else:
                self.image = self.jump_frames_right[self.frame]
        # idle
        elif self.state == 'idle':
            if self.frame > self.idle_frames_length - 1:
                self.frame = 0

            if self.direction == 'L':
                self.image = self.idle_frames_left[self.frame]
            else:
                self.image = self.idle_frames_right[self.frame]

    def load_frames(self, path, length):
        left = []
        right = []

        for i in range(length):
            image = pygame.image.load(path + f'{i+1}.png').convert_alpha()
            right.append(image)
            left.append(pygame.transform.flip(image, True, False))

        return left, right

