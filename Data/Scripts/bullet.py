import pygame


class Bullet:
    def __init__(self, velocity, position, wall):
        self.velocity = velocity
        self.position = position
        self.wall = wall
        self.image = pygame.image.load('Data/Assets/Sprites/Bullets/bullet.png').convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.center = position
        self.sparkle_frames_length = 8
        self.frame = 0
        self.frame_change = .1
        self.frame_count = 0

        self.glow_color = (20, 0, 44)

        self.big_glow_size = self.rect.width * 2
        self.small_glow_size = self.rect.width * 1.5

        self.glow_grow = True
        self.dead = False
        self.sparkle_done = False

        self.sparkle_frames = []
        for i in range(self.sparkle_frames_length):
            image = pygame.image.load(f'Data/Assets/Sprites/Bullets/Sparkle/sparkle_{i + 1}.png').convert_alpha()

            if self.wall == 2:
                self.sparkle_frames.append(image)
            elif self.wall == 1:
                self.sparkle_frames.append(pygame.transform.rotate(image, 90))
            else:
                self.sparkle_frames.append(pygame.transform.flip(image, True, False))

        self.sparkle_image = self.sparkle_frames[0]

        if self.wall == 0:
            self.render_x = position[0]
            self.render_y = position[1] - self.sparkle_image.get_height() / 2
        elif self.wall == 1:
            self.render_x = position[0] - self.sparkle_image.get_width() / 2
            self.render_y = position[1]
        else:
            self.render_x = position[0] - self.sparkle_image.get_width()
            self.render_y = position[1] - self.sparkle_image.get_height() / 2

    def update(self, surface, paused):
        if not paused:
            # move
            self.position[0] += self.velocity[0]
            self.position[1] += self.velocity[1]
            self.rect.center = self.position

            if not self.sparkle_done:
                self.draw_sparkle(surface)

            self.check_dead()

        if not self.dead:

            glow_big, glow_small = self.get_glow()

            surface.blit(glow_big, (self.rect.center[0] - self.big_glow_size, self.rect.center[1] - self.big_glow_size), special_flags=pygame.BLEND_RGB_ADD)
            surface.blit(glow_small, (self.rect.center[0] - self.small_glow_size, self.rect.center[1] - self.small_glow_size), special_flags=pygame.BLEND_RGB_ADD)
            surface.blit(self.image, self.rect)

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

    def check_dead(self):
        if self.rect.center[0] + self.big_glow_size < 0:
            self.dead = True
        elif self.rect.center[0] - self.big_glow_size > 512:
            self.dead = True
        elif self.rect.center[1] + self.big_glow_size < 0:
            self.dead = True
        elif self.rect.center[1] - self.big_glow_size > 288:
            self.dead = True

    def draw_sparkle(self, surface):
        self.frame_count += 1
        if self.frame_count / 60 >= self.frame_change:
            self.frame_count = 0
            self.frame += 1

            if self.frame == self.sparkle_frames_length - 1:
                self.sparkle_done = True
                return

            self.sparkle_image = self.sparkle_frames[self.frame]

        surface.blit(self.sparkle_image, (self.render_x, self.render_y))

