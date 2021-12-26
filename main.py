import pygame
import random
import json

from Data.Scripts import colors, rock_handler, bullet_handler, player, hud


class Game:
    def __init__(self):
        pygame.init()

        # bool
        self.running = True
        self.round_over = False
        self.paused = False
        self.checked_for_new_highscore = False
        self.new_highscore = False

        # numbers
        self.screen_width = 1920
        self.screen_height = 1080

        self.render_width = 512
        self.render_height = 288

        self.background_lines_width = 10
        self.background_lines_distance = 20
        self.background_lines_yoffset = -30
        self.background_lines_speed = -1
        self.background_rects_max_size = 64
        self.background_rects_min_size = 32
        self.background_rects_speed = 1
        self.background_rects_rotation_speed = 1

        self.map_shadow_speed = 1
        self.map_shadow_change_speed = 0.2

        self.map_shadow_lr_60_count = random.randint(0, 60)
        self.map_shadow_lr_60_frame = random.randint(0, 2)
        self.map_shadow_lr_20_count = random.randint(0, 60)
        self.map_shadow_lr_20_frame = random.randint(0, 2)

        self.map_shadow_b_60_count = random.randint(0, 60)
        self.map_shadow_b_60_frame = random.randint(0, 2)
        self.map_shadow_b_20_count = random.randint(0, 60)
        self.map_shadow_b_20_frame = random.randint(0, 2)

        self.map_shadow_t_60_count = random.randint(0, 60)
        self.map_shadow_t_60_frame = random.randint(0, 2)
        self.map_shadow_t_20_count = random.randint(0, 60)
        self.map_shadow_t_20_frame = random.randint(0, 2)

        self.highscore = 0

        # iterable
        self.screen_dimensions = (self.screen_width, self.screen_height)
        self.render_dimensions = (self.render_width, self.render_height)

        self.player_spawn = (self.render_width / 2, self.render_height / 2)

        self.items = []
        self.particles = []

        with open('Data/Files/gamesave.json', 'r') as f:
            self.game_save = json.load(f)
            self.highscore = self.game_save['highscore']

        # objects
        screen_flags = pygame.DOUBLEBUF, pygame.HWSURFACE
        self.screen = pygame.display.set_mode(self.screen_dimensions, *screen_flags)
        pygame.display.set_caption('TempleDodge')
        pygame.display.set_icon(pygame.image.load('Data/Assets/Sprites/Gui/icon.png'))
        self.screen.set_colorkey(colors.black)
        self.clock = pygame.time.Clock()
        self.render_surface = pygame.Surface(self.render_dimensions).convert_alpha()
        self.render_surface.set_colorkey(colors.black)
        self.rock_handler = rock_handler.RockHandler(10, 0)
        self.bullet_handler = bullet_handler.BulletHandler(1, 5, 20, 10)
        self.player = player.Player(self.player_spawn, self.rock_handler.landed_rocks, self.rock_handler.falling_rocks, self.rock_handler.chests, self.items, self.bullet_handler.bullets)
        self.hud = hud.Hud(self.player)

        # dependent lists
        self.chests = self.rock_handler.chests

        # images
        self.background_rect_image = pygame.image.load("Data/Assets/Sprites/Background/rect.png").convert_alpha()

        self.map_shadow_image_lr_20_0 = pygame.image.load("Data/Assets/Sprites/Map/wallshadow_lr_20_1.png").convert_alpha()
        self.map_shadow_image_lr_20_1 = pygame.image.load("Data/Assets/Sprites/Map/wallshadow_lr_20_2.png").convert_alpha()
        self.map_shadow_image_lr_20_2 = pygame.image.load("Data/Assets/Sprites/Map/wallshadow_lr_20_3.png").convert_alpha()

        self.map_shadow_image_lr_60_0 = pygame.image.load("Data/Assets/Sprites/Map/wallshadow_lr_60_1.png").convert_alpha()
        self.map_shadow_image_lr_60_1 = pygame.image.load("Data/Assets/Sprites/Map/wallshadow_lr_60_2.png").convert_alpha()
        self.map_shadow_image_lr_60_2 = pygame.image.load("Data/Assets/Sprites/Map/wallshadow_lr_60_3.png").convert_alpha()

        self.map_shadow_image_b_20_0 = pygame.image.load("Data/Assets/Sprites/Map/wallshadow_b_20_1.png").convert_alpha()
        self.map_shadow_image_b_20_1 = pygame.image.load("Data/Assets/Sprites/Map/wallshadow_b_20_2.png").convert_alpha()
        self.map_shadow_image_b_20_2 = pygame.image.load("Data/Assets/Sprites/Map/wallshadow_b_20_3.png").convert_alpha()

        self.map_shadow_image_b_60_0 = pygame.image.load("Data/Assets/Sprites/Map/wallshadow_b_60_1.png").convert_alpha()
        self.map_shadow_image_b_60_1 = pygame.image.load("Data/Assets/Sprites/Map/wallshadow_b_60_2.png").convert_alpha()
        self.map_shadow_image_b_60_2 = pygame.image.load("Data/Assets/Sprites/Map/wallshadow_b_60_3.png").convert_alpha()

        self.map_shadow_image_t_20_0 = pygame.image.load("Data/Assets/Sprites/Map/wallshadow_t_20_1.png").convert_alpha()
        self.map_shadow_image_t_20_1 = pygame.image.load("Data/Assets/Sprites/Map/wallshadow_t_20_2.png").convert_alpha()
        self.map_shadow_image_t_20_2 = pygame.image.load("Data/Assets/Sprites/Map/wallshadow_t_20_3.png").convert_alpha()

        self.map_shadow_image_t_60_0 = pygame.image.load("Data/Assets/Sprites/Map/wallshadow_t_60_1.png").convert_alpha()
        self.map_shadow_image_t_60_1 = pygame.image.load("Data/Assets/Sprites/Map/wallshadow_t_60_2.png").convert_alpha()
        self.map_shadow_image_t_60_2 = pygame.image.load("Data/Assets/Sprites/Map/wallshadow_t_60_3.png").convert_alpha()

        self.map_border_image = pygame.image.load("Data/Assets/Sprites/Map/walls.png").convert_alpha()

        # dependent setups
        self.background_lines = self.make_background_lines()
        self.background_rects = self.make_background_rects()
        self.map_shadow_lr_ys = [0, -self.map_shadow_image_lr_20_0.get_height()]
        self.map_shadow_b_xs = [0, self.map_shadow_image_b_20_0.get_width()]
        self.map_shadow_t_xs = [0, -self.map_shadow_image_t_20_0.get_width()]
        self.map_shadow_b_y = self.render_height - self.map_shadow_image_b_20_0.get_height()

    def run(self):
        while self.running:
            self.clock.tick(60)
            self.screen.fill('black')
            # input
            self.handle_input()
            # background
            self.draw_background(self.render_surface)

            # entitys in right order
            self.rock_handler.update(True, self.render_surface, self.paused)
            self.update_chests(self.render_surface)
            self.player.update(self.render_surface, self.paused)
            self.update_items(self.render_surface)
            self.bullet_handler.update(self.render_surface, self.paused)
            self.hud.update(self.render_surface, self.paused)

            if self.player.dead:
                if not self.checked_for_new_highscore:
                    self.check_highscore()
                    self.hud.render_dead(self.player.gold_count, self.highscore)
                self.hud.display_dead(self.render_surface, self.new_highscore)

            # map shadows
            self.draw_map_shadows(self.render_surface)

            # scale image
            self.screen.blit(pygame.transform.scale(self.render_surface, self.screen_dimensions), (0, 0))
            # update screen
            pygame.display.update()

    def handle_input(self):
        for event in pygame.event.get():
            # quit event
            if event.type == pygame.QUIT:
                self.exit()
            # keypresses
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.player.jump()
                elif event.key == pygame.K_f:
                    self.player.enable_ghost_mode()
                elif event.key == pygame.K_ESCAPE:
                    if not self.round_over:
                        if self.paused:
                            self.paused = False
                        else:
                            self.paused = True
                elif event.key == pygame.K_r:
                    if self.player.dead:
                        self.prepare_new_round()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            self.player.go_left()
        if keys[pygame.K_d]:
            self.player.go_right()
        if keys[pygame.K_s]:
            self.player.go_down()
        if keys[pygame.K_w]:
            self.player.go_up()
        if (keys[pygame.K_a] and keys[pygame.K_d]) or (not keys[pygame.K_a] and not keys[pygame.K_d]):
            self.player.stop()
        if (keys[pygame.K_w] and keys[pygame.K_s]) or (not keys[pygame.K_w] and not keys[pygame.K_s]):
            self.player.stop_ghost_y()

    def update_chests(self, surface):
        to_remove = []
        # handle chests
        for entity in self.chests:
            if not entity.done:
                entity.update(surface, self.rock_handler.falling_rocks)

                if entity.opened and len(entity.items) > 0:
                    self.items += entity.items
                    entity.items.clear()

                if entity.opened and len(entity.particles) > 0:
                    self.particles += entity.particles
                    entity.particles.clear()

            else:
                to_remove.append(entity)

        # remove done chests
        for entity in to_remove:
            self.chests.remove(entity)

    def update_items(self, surface):
        to_remove = []
        # handle items
        for entity in self.items:
            if entity.collected:
                to_remove.append(entity)
            else:
                entity.update(surface, self.paused)

        for entity in to_remove:
            self.items.remove(entity)

    def draw_background(self, surface):
        # base color
        surface.fill(colors.grey_4)

        # rects
        for rect in self.background_rects:
            render = pygame.transform.rotate(rect[0], rect[3]).convert_alpha()

            rect[1][1] += self.background_rects_speed
            if rect[3] > 0:
                rect[3] += self.background_rects_rotation_speed
            elif rect[3] < 0:
                rect[3] -= self.background_rects_rotation_speed

            if self.background_rects_speed > 0 and rect[1][1] - render.get_height() / 2 > self.render_height:
                min_y = min([i[1][1] for i in self.background_rects if i[1][0] == rect[1][0]])
                rect[1][1] = min_y - self.render_height / 3
            elif self.background_rects_speed < 0 and rect[1][1] + render.get_height() / 2 < 0:
                max_y = max([i[1][1] for i in self.background_rects if i[1][0] == rect[1][0]])
                rect[1][1] = max_y + self.render_height / 3

            render_x = rect[1][0] - render.get_width() / 2
            render_y = rect[1][1] - render.get_height() / 2
            surface.blit(render, (round(render_x) - 5, round(render_y) + 5), special_flags=pygame.BLEND_RGB_SUB)
            surface.blit(render, (round(render_x), round(render_y)))

        # lines
        for line in self.background_lines:
            line[0][1] += self.background_lines_speed
            line[1][1] += self.background_lines_speed

            if self.background_lines_speed > 0 and min([line[0][1], line[1][1]]) > self.render_height:
                min_line_y = min([i[0][1] for i in self.background_lines])
                new_y = min_line_y - 2 * self.background_lines_distance
                line[0][1] = new_y
                line[1][1] = new_y + self.background_lines_yoffset

            elif self.background_lines_speed < 0 and max([line[0][1], line[1][1]]) < 0:
                max_line_y = max([i[0][1] for i in self.background_lines])
                new_y = max_line_y + 2 * self.background_lines_distance
                line[0][1] = new_y
                line[1][1] = new_y + self.background_lines_yoffset

            shadow_color = (12, 12, 12)
            shadow_start = [line[0][0], line[0][1] + 5]
            shadow_end = [line[1][0], line[1][1] + 5]
            pygame.draw.line(surface, shadow_color, shadow_start, shadow_end, self.background_lines_width)
            pygame.draw.line(surface, colors.grey_6, line[0], line[1], self.background_lines_width)

        # map border
        surface.blit(self.map_border_image, (0, 0))

    def draw_map_shadows(self, surface):
        # left and right
        self.map_shadow_lr_ys[0] += self.map_shadow_speed
        self.map_shadow_lr_ys[1] += self.map_shadow_speed

        if self.map_shadow_lr_ys[0] > self.render_height:
            self.map_shadow_lr_ys[0] -= self.map_shadow_image_lr_20_0.get_height() * 2
        elif self.map_shadow_lr_ys[1] > self.render_height:
            self.map_shadow_lr_ys[1] -= self.map_shadow_image_lr_20_0.get_height() * 2

        if self.map_shadow_lr_60_count / 60 >= self.map_shadow_change_speed:
            self.map_shadow_lr_60_count = 0
            self.map_shadow_lr_60_frame += 1
            if self.map_shadow_lr_60_frame >= 3:
                self.map_shadow_lr_60_frame = 0
        self.map_shadow_lr_60_count += 1

        if self.map_shadow_lr_20_count / 60 >= self.map_shadow_change_speed:
            self.map_shadow_lr_20_count = 0
            self.map_shadow_lr_20_frame += 1
            if self.map_shadow_lr_20_frame >= 3:
                self.map_shadow_lr_20_frame = 0
        self.map_shadow_lr_20_count += 1

        for y in self.map_shadow_lr_ys:
            if self.map_shadow_lr_60_frame == 0:
                surface.blit(self.map_shadow_image_lr_60_0, (0, y), special_flags=pygame.BLEND_RGB_SUB)
            elif self.map_shadow_lr_60_frame == 1:
                surface.blit(self.map_shadow_image_lr_60_1, (0, y), special_flags=pygame.BLEND_RGB_SUB)
            else:
                surface.blit(self.map_shadow_image_lr_60_2, (0, y), special_flags=pygame.BLEND_RGB_SUB)

            if self.map_shadow_lr_20_frame == 0:
                surface.blit(self.map_shadow_image_lr_20_0, (0, y))
            elif self.map_shadow_lr_20_frame == 1:
                surface.blit(self.map_shadow_image_lr_20_1, (0, y))
            else:
                surface.blit(self.map_shadow_image_lr_20_2, (0, y))

        # top
        self.map_shadow_t_xs[0] += self.map_shadow_speed
        self.map_shadow_t_xs[1] += self.map_shadow_speed

        if self.map_shadow_t_xs[0] > self.render_width:
            self.map_shadow_t_xs[0] -= self.map_shadow_image_t_20_0.get_width() * 2
        elif self.map_shadow_t_xs[1] > self.render_width:
            self.map_shadow_t_xs[1] -= self.map_shadow_image_t_20_0.get_width() * 2

        if self.map_shadow_t_60_count / 60 >= self.map_shadow_change_speed:
            self.map_shadow_t_60_count = 0
            self.map_shadow_t_60_frame += 1
            if self.map_shadow_t_60_frame >= 3:
                self.map_shadow_t_60_frame = 0
        self.map_shadow_t_60_count += 1

        if self.map_shadow_t_20_count / 60 >= self.map_shadow_change_speed:
            self.map_shadow_t_20_count = 0
            self.map_shadow_t_20_frame += 1
            if self.map_shadow_t_20_frame >= 3:
                self.map_shadow_t_20_frame = 0
        self.map_shadow_t_20_count += 1

        for x in self.map_shadow_t_xs:
            if self.map_shadow_t_60_frame == 0:
                surface.blit(self.map_shadow_image_t_60_0, (x, 0), special_flags=pygame.BLEND_RGB_SUB)
            elif self.map_shadow_t_60_frame == 1:
                surface.blit(self.map_shadow_image_t_60_1, (x, 0), special_flags=pygame.BLEND_RGB_SUB)
            else:
                surface.blit(self.map_shadow_image_t_60_2, (x, 0), special_flags=pygame.BLEND_RGB_SUB)

            if self.map_shadow_t_20_frame == 0:
                surface.blit(self.map_shadow_image_t_20_0, (x, 0))
            elif self.map_shadow_t_20_frame == 1:
                surface.blit(self.map_shadow_image_t_20_1, (x, 0))
            else:
                surface.blit(self.map_shadow_image_t_20_2, (x, 0))

        # bottom
        self.map_shadow_b_xs[0] -= self.map_shadow_speed
        self.map_shadow_b_xs[1] -= self.map_shadow_speed

        if self.map_shadow_b_xs[0] + self.map_shadow_image_b_20_0.get_width() < 0:
            self.map_shadow_b_xs[0] += self.map_shadow_image_b_20_0.get_width() * 2
        elif self.map_shadow_b_xs[1] + self.map_shadow_image_b_20_0.get_width() < 0:
            self.map_shadow_b_xs[1] += self.map_shadow_image_b_20_0.get_width() * 2

        if self.map_shadow_b_60_count / 60 >= self.map_shadow_change_speed:
            self.map_shadow_b_60_count = 0
            self.map_shadow_b_60_frame += 1
            if self.map_shadow_b_60_frame >= 3:
                self.map_shadow_b_60_frame = 0
        self.map_shadow_b_60_count += 1

        if self.map_shadow_b_20_count / 60 >= self.map_shadow_change_speed:
            self.map_shadow_b_20_count = 0
            self.map_shadow_b_20_frame += 1
            if self.map_shadow_b_20_frame >= 3:
                self.map_shadow_b_20_frame = 0
        self.map_shadow_b_20_count += 1

        for x in self.map_shadow_b_xs:
            if self.map_shadow_b_60_frame == 0:
                surface.blit(self.map_shadow_image_b_60_0, (x, self.map_shadow_b_y), special_flags=pygame.BLEND_RGB_SUB)
            elif self.map_shadow_b_60_frame == 1:
                surface.blit(self.map_shadow_image_b_60_1, (x, self.map_shadow_b_y), special_flags=pygame.BLEND_RGB_SUB)
            else:
                surface.blit(self.map_shadow_image_b_60_2, (x, self.map_shadow_b_y), special_flags=pygame.BLEND_RGB_SUB)

            if self.map_shadow_b_20_frame == 0:
                surface.blit(self.map_shadow_image_b_20_0, (x, self.map_shadow_b_y))
            if self.map_shadow_b_20_frame == 1:
                surface.blit(self.map_shadow_image_b_20_1, (x, self.map_shadow_b_y))
            else:
                surface.blit(self.map_shadow_image_b_20_2, (x, self.map_shadow_b_y))

    def make_background_lines(self):
        lines = []
        number_of_lines = round(self.render_height/self.background_lines_distance/2) + 2
        for i in range(number_of_lines):
            y = (i - 2) * (2 * self.background_lines_distance)
            left_point = [0, y]
            right_point = [self.render_width, y + self.background_lines_yoffset]
            lines.append([left_point, right_point])
        return lines

    def make_background_rects(self):
        rects = []
        for i in range(15):
            size = random.randint(self.background_rects_min_size, self.background_rects_max_size)
            rotation = random.randint(-180, 180)
            image = pygame.transform.scale(self.background_rect_image, (size, size)).convert_alpha()

            if i < 5:
                y = (i + 1) * (self.render_height / 3)
                x = self.render_width / 4
            elif i < 10:
                y = (i - 5 + 1.3) * (self.render_height / 3)
                x = (self.render_width / 4) * 2
            else:
                y = (i - 10 + 1.6) * self.render_height / 3
                x = (self.render_width / 4) * 3

            rects.append([image, [x, y], size, rotation])
        return rects

    def prepare_new_round(self):
        self.checked_for_new_highscore = False
        self.new_highscore = False
        self.player.reset(self.player_spawn)
        self.rock_handler.reset()
        self.bullet_handler.reset()
        self.items.clear()

    def check_highscore(self):
        self.checked_for_new_highscore = True
        if self.highscore < self.player.gold_count:
            self.new_highscore = True
            self.game_save['highscore'] = self.player.gold_count
            self.highscore = self.player.gold_count

    def exit(self):
        # save
        with open('Data/Files/gamesave.json', 'w') as f:
            json.dump(self.game_save, f, indent=4)
        # exit
        self.running = False


if __name__ == '__main__':
    game = Game()
    game.run()
