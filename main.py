import json
import os
import random
import time

import pygame

from Data.Scripts import colors, rock_handler, bullet_handler, player, hud, funcs


# Game object:
# basically represents the applications object and holds all other game objects
class Game:
    def __init__(self):
        # init pygame before using it
        pygame.init()

        # hide mouse
        pygame.mouse.set_visible(False)

        self.running = True
        self.paused = True
        self.first_time = True
        self.checked_for_new_highscore = False
        self.new_highscore = False

        # size of the screen
        self.screen_width = 1920
        self.screen_height = 1080

        # size of the render surface which we than scale to screen size
        self.render_width = 512
        self.render_height = 288

        # self explaining variables for the background lines and rects
        self.background_lines_width = 10
        self.background_lines_distance = 20
        self.background_lines_yoffset = -30
        self.background_lines_speed = -1
        self.background_rects_max_size = 64
        self.background_rects_min_size = 32
        self.background_rects_speed = 1
        self.background_rects_rotation_speed = 1

        # same for 'shadows' around the map
        self.map_shadow_speed = 1
        self.map_shadow_change_speed = 0.2

        # count raises with every frame until to keep track when so switch to the next frame
        # count and frames are randomized to make the shadows feel more 'smooth'
        # variable names represent map_shadow + the side they are at + their rgb value + frame / count
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

        # packed width and height in tuples for easier access
        self.screen_dimensions = (self.screen_width, self.screen_height)
        self.render_dimensions = (self.render_width, self.render_height)

        self.player_spawn = (self.render_width / 2, self.render_height / 2)

        self.items = []

        # check if the gamesave.json file exists
        # then either read from it or create it
        if os.path.exists('Data/Files/gamesave.json'):
            with open('Data/Files/gamesave.json', 'r') as f:
                self.game_save = json.load(f)
                self.highscore = self.game_save['highscore']
        else:
            self.game_save = {"highscore": 0}
            self.highscore = 0
            with open('Data/Files/gamesave.json', 'w') as f:
                json.dump(self.game_save, f, indent=4)

        # screen_flags are just some special modes for the window
        screen_flags = pygame.DOUBLEBUF, pygame.HWSURFACE

        # create screen object and apply title and icon and set a color key for transparency
        self.screen = pygame.display.set_mode(self.screen_dimensions, *screen_flags)
        pygame.display.set_caption('TempleDodge')
        pygame.display.set_icon(pygame.image.load('Data/Assets/Sprites/Gui/icon.png'))
        self.screen.set_colorkey(colors.black)

        # clock object keeps track of refresh rate
        self.clock = pygame.time.Clock()
        self.fps = 60

        # render surface will hold the original frame
        self.render_surface = pygame.Surface(self.render_dimensions).convert_alpha()
        self.render_surface.set_colorkey(colors.black)

        # rect where no particles should be drawn while the hud shows a message
        topleft = funcs.render_pos_to_screen_pos((108, 64), self.screen_dimensions)
        bottomright = funcs.render_pos_to_screen_pos((404, 224), self.screen_dimensions)
        self.no_particle_rect = pygame.Rect(topleft, (bottomright[0] - topleft[0], bottomright[1] - topleft[1]))

        # handles all the stone blocks that fall down in game
        self.rock_handler = rock_handler.RockHandler(5)

        # does the same for the purple projectiles
        self.bullet_handler = bullet_handler.BulletHandler(1, 15, 60, 10)

        self.player = player.Player(self.player_spawn, self.rock_handler.landed_rocks, self.rock_handler.falling_rocks, self.rock_handler.chests, self.items, self.bullet_handler.bullets)
        self.hud = hud.Hud(self.player)

        # point to the list that will hold all the chests
        self.chests = self.rock_handler.chests

        # all the necessary images for the background and the 'shadows' around the map + the left and right border of the map
        self.background_rect_image = pygame.image.load("Data/Assets/Sprites/Background/rect.png").convert_alpha()
        self.background_rect_shadow_image = pygame.image.load("Data/Assets/Sprites/Background/rect_shadow.png").convert_alpha()

        self.map_shadow_image_l_20_0 = pygame.image.load("Data/Assets/Sprites/Map/wallshadow_l_20_1.png").convert_alpha()
        self.map_shadow_image_l_20_1 = pygame.image.load("Data/Assets/Sprites/Map/wallshadow_l_20_2.png").convert_alpha()
        self.map_shadow_image_l_20_2 = pygame.image.load("Data/Assets/Sprites/Map/wallshadow_l_20_3.png").convert_alpha()

        self.map_shadow_image_r_20_0 = pygame.image.load("Data/Assets/Sprites/Map/wallshadow_r_20_1.png").convert_alpha()
        self.map_shadow_image_r_20_1 = pygame.image.load("Data/Assets/Sprites/Map/wallshadow_r_20_2.png").convert_alpha()
        self.map_shadow_image_r_20_2 = pygame.image.load("Data/Assets/Sprites/Map/wallshadow_r_20_3.png").convert_alpha()

        self.map_shadow_image_l_60_0 = pygame.image.load("Data/Assets/Sprites/Map/wallshadow_l_60_1.png").convert_alpha()
        self.map_shadow_image_l_60_1 = pygame.image.load("Data/Assets/Sprites/Map/wallshadow_l_60_2.png").convert_alpha()
        self.map_shadow_image_l_60_2 = pygame.image.load("Data/Assets/Sprites/Map/wallshadow_l_60_3.png").convert_alpha()

        self.map_shadow_image_r_60_0 = pygame.image.load("Data/Assets/Sprites/Map/wallshadow_r_60_1.png").convert_alpha()
        self.map_shadow_image_r_60_1 = pygame.image.load("Data/Assets/Sprites/Map/wallshadow_r_60_2.png").convert_alpha()
        self.map_shadow_image_r_60_2 = pygame.image.load("Data/Assets/Sprites/Map/wallshadow_r_60_3.png").convert_alpha()

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

        # call constructor functions which will create lists representing the lines or the rects for the background
        self.background_lines = self.make_background_lines()
        self.background_rects = self.make_background_rects()

        self.line_shadow_color = (12, 12, 12)

        # set x and y values for the 'shadows' based or the image dimensions
        self.map_shadow_lr_ys = [0, -self.map_shadow_image_l_20_0.get_height()]
        self.map_shadow_lr_xs = [0, self.render_width - self.map_shadow_image_l_20_0.get_width()]
        self.map_shadow_b_xs = [0, self.map_shadow_image_b_20_0.get_width()]
        self.map_shadow_t_xs = [0, -self.map_shadow_image_t_20_0.get_width()]
        self.map_shadow_b_y = self.render_height - self.map_shadow_image_b_20_0.get_height()

        # load the background music track, set the volume to 10% and play it endless
        pygame.mixer.music.load('Data/Assets/Sound/BackgroundMusic/background_music_1.wav')
        pygame.mixer.music.set_volume(.1)
        pygame.mixer.music.play(-1)

        self.last_time = time.time()
        # dt = delta time --> represented time between two frames
        self.dt = 0

    # the run function holds the main game loop
    def run(self):
        # this is the main game loop
        # it gets updated once per frame
        while self.running:
            # clock keeps the game from overshoot the fps
            self.clock.tick(self.fps)
            #print(self.clock.get_fps())

            # determine delta time which is mostly used with movement to compensate slower fps
            self.dt = time.time() - self.last_time
            self.dt *= 60
            self.last_time = time.time()

            # prevent game braking low fps
            if self.dt > 16:
                raise RuntimeWarning("FPS fallen below playable limit")

            # handle all key presses
            self.handle_input()

            # draw the background
            self.draw_background(self.render_surface)

            # this updates all the objects in the order they get drawn onto the render surface
            self.rock_handler.update(True, self.render_surface, self.paused)
            self.update_chests(self.render_surface)
            self.update_items(self.render_surface)
            self.player.update(self.render_surface, self.paused)
            self.bullet_handler.update(self.render_surface, self.paused)
            self.hud.update(self.render_surface, self.paused)

            # if the player is dead
            if self.player.dead:
                # look if it is a new highscore and render the hud message if we did not already done it
                if not self.checked_for_new_highscore:
                    self.check_highscore()
                    self.hud.render_dead(self.player.gold_count, self.highscore)
                # display the message on the screen
                self.hud.display_dead(self.render_surface, self.new_highscore)

            # draw the 'shadows' on top of everything
            self.draw_map_shadows(self.render_surface)

            # now scale the render to screen size and draw in to the actual screen
            self.screen.blit(pygame.transform.scale(self.render_surface, self.screen_dimensions), (0, 0))

            # now draw all the particle object that every player and rock etc. hold
            # they do not get drawn onto the screen and not the render surface to look smaller
            # because they do not get scaled
            self.rock_handler.update_particles(self.screen, self.paused, self.player.dead, self.no_particle_rect)
            self.player.update_particles(self.screen, self.paused, self.no_particle_rect)
            self.update_item_particles(self.screen)
            self.update_chest_particles(self.screen)
            self.bullet_handler.update_particles(self.screen, self.paused, self.player.dead, self.no_particle_rect)

            # at the end update the screen to show the changes
            pygame.display.flip()

    # handles all the key presses and other events
    def handle_input(self):
        # get all events and check for their type
        for event in pygame.event.get():
            # if the player presses the x on the window or uses alt + f4
            # we call  the exit function
            if event.type == pygame.QUIT:
                self.exit()
            # if the player presses a key we check which one it was (event.key)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    # space is used to start the game the first time
                    if self.paused:
                        if self.first_time:
                            self.first_time = False
                            self.paused = False
                            self.hud.first_time = False
                    # and lets the player jump
                    else:
                        self.player.jump()
                # the f key activates the players power
                elif event.key == pygame.K_f:
                    self.player.enable_ghost_mode()
                # escape pauses or unpauses the game
                elif event.key == pygame.K_ESCAPE:
                    if not self.player.dead:
                        if self.paused:
                            self.paused = False
                        else:
                            self.paused = True
                # and the r key starts a new round
                elif event.key == pygame.K_r:
                    if self.player.dead:
                        self.prepare_new_round()

        # check all the keys that are being hold
        # move the player in the direction or stop him if the directions cancel each other out
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

    # updates every chest object
    def update_chests(self, surface):
        to_remove = []
        # handle chests
        for entity in self.chests:
            # update it and get all the items in our list
            # or move the chest to the ones that needs to be removed
            if not entity.done:
                entity.update(surface)

                if entity.opened and len(entity.items) > 0:
                    self.items += entity.items
                    entity.items.clear()

            else:
                to_remove.append(entity)

        # remove the chests that are done
        for entity in to_remove:
            self.chests.remove(entity)

    # now do the same updating and deleting for the items we grabbed from the chests
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

    # update all particles from out items
    def update_item_particles(self, surface):
        for entity in self.items:
            entity.update_particles(surface, self.paused, self.player.dead, self.no_particle_rect)

    # same for the chests
    def update_chest_particles(self, surface):
        for entity in self.chests:
            entity.update_particles(surface, self.paused, self.player.dead, self.no_particle_rect)

    # draws the background rects and lines
    def draw_background(self, surface):
        # fill the background with the base color
        surface.fill(colors.grey_4)

        # draw all the rects
        for rect in self.background_rects:
            # get the rotates image from the rect and its shadow
            render = pygame.transform.rotate(rect[0], rect[4])
            shadow_render = pygame.transform.rotate(rect[1], rect[4])

            # change the rects y position and change the rotation for the next frame
            rect[2][1] += self.background_rects_speed * self.dt
            if rect[4] > 0:
                rect[4] += self.background_rects_rotation_speed * self.dt
                if rect[4] > 360:
                    rect[4] -= 360
            elif rect[4] < 0:
                rect[4] -= self.background_rects_rotation_speed * self.dt
                if rect[4] < -360:
                    rect[4] += 360

            # move rect if off screen
            # if they move down set the rect over the highest one
            # otherwise under the lowest one
            if self.background_rects_speed > 0 and rect[2][1] - render.get_height() / 2 > self.render_height:
                min_y = min([i[2][1] for i in self.background_rects if i[2][0] == rect[2][0]])
                rect[2][1] = min_y - self.render_height / 3
            elif self.background_rects_speed < 0 and rect[2][1] + render.get_height() / 2 < 0:
                max_y = max([i[2][1] for i in self.background_rects if i[2][0] == rect[2][0]])
                rect[2][1] = max_y + self.render_height / 3

            # set the render position based ont he dimensions of the rotated images and draw the rect on the render surface
            render_x = rect[2][0] - render.get_width() / 2
            render_y = rect[2][1] - render.get_height() / 2
            surface.blit(shadow_render, (round(render_x) - 5, round(render_y) + 5))
            surface.blit(render, (round(render_x), round(render_y)))

        # draw the lines on top of the rects
        # first tilt the lines matching the players position in relation to the screens center
        self.background_lines_yoffset = (self.player.rect.x - self.render_width / 2) / 3

        # update and draw each line
        for line in self.background_lines:
            # move the lines start and endpoints y position
            line[0][1] += self.background_lines_speed * self.dt
            line[1][1] = line[0][1] + self.background_lines_yoffset

            # if the line is off screen
            # if they if they move down set the line over the highest one
            # otherwise under the lowest one
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

            # set the points for the lines shadow slightly under the line
            shadow_start = [line[0][0], line[0][1] + 5]
            shadow_end = [line[1][0], line[1][1] + 5]

            # draw the lines shadow, than the line itself
            pygame.draw.line(surface, self.line_shadow_color, shadow_start, shadow_end, self.background_lines_width)
            pygame.draw.line(surface, colors.grey_6, line[0], line[1], self.background_lines_width)

        # dra the map border image
        surface.blit(self.map_border_image, (0, 0))

    # draws the map 'shadow' cloud things around the map
    # the functions moves the images over the screen and draws a second image behind every one to keep the endless effect
    # while it changes the between the frames
    def draw_map_shadows(self, surface):
        # first doe the ones on the left and right
        # move their y value
        self.map_shadow_lr_ys[0] += self.map_shadow_speed * self.dt
        self.map_shadow_lr_ys[1] += self.map_shadow_speed * self.dt

        # if one of the y values is off the screen it moves it behind the other one
        if self.map_shadow_lr_ys[0] > self.render_height:
            self.map_shadow_lr_ys[0] -= self.map_shadow_image_l_20_0.get_height() * 2
        elif self.map_shadow_lr_ys[1] > self.render_height:
            self.map_shadow_lr_ys[1] -= self.map_shadow_image_l_20_0.get_height() * 2

        # count the refreshes since the last frame change
        # change the frame if it is time to do so
        self.map_shadow_lr_60_count += 1 * self.dt
        if self.map_shadow_lr_60_count / 60 >= self.map_shadow_change_speed:
            self.map_shadow_lr_60_count = 0
            self.map_shadow_lr_60_frame += 1
            # prevent the map frame from going over the frames available
            if self.map_shadow_lr_60_frame >= 3:
                self.map_shadow_lr_60_frame = 0

        # do the same for the images with the other rgb value
        self.map_shadow_lr_20_count += 1 * self.dt
        if self.map_shadow_lr_20_count / 60 >= self.map_shadow_change_speed:
            self.map_shadow_lr_20_count = 0
            self.map_shadow_lr_20_frame += 1
            if self.map_shadow_lr_20_frame >= 3:
                self.map_shadow_lr_20_frame = 0

        # draw the images based on the current frame
        # the special flag shifts all the pixels rgb values under the images down
        # and creates the transparent shadow effect
        for y in self.map_shadow_lr_ys:
            if self.map_shadow_lr_60_frame == 0:
                surface.blit(self.map_shadow_image_l_60_0, (self.map_shadow_lr_xs[0], y), special_flags=pygame.BLEND_RGB_SUB)
                surface.blit(self.map_shadow_image_r_60_0, (self.map_shadow_lr_xs[1], y), special_flags=pygame.BLEND_RGB_SUB)
            elif self.map_shadow_lr_60_frame == 1:
                surface.blit(self.map_shadow_image_l_60_1, (self.map_shadow_lr_xs[0], y), special_flags=pygame.BLEND_RGB_SUB)
                surface.blit(self.map_shadow_image_r_60_1, (self.map_shadow_lr_xs[1], y), special_flags=pygame.BLEND_RGB_SUB)
            else:
                surface.blit(self.map_shadow_image_l_60_2, (self.map_shadow_lr_xs[0], y), special_flags=pygame.BLEND_RGB_SUB)
                surface.blit(self.map_shadow_image_r_60_2, (self.map_shadow_lr_xs[1], y), special_flags=pygame.BLEND_RGB_SUB)

            if self.map_shadow_lr_20_frame == 0:
                surface.blit(self.map_shadow_image_l_20_0, (self.map_shadow_lr_xs[0], y))
                surface.blit(self.map_shadow_image_r_20_0, (self.map_shadow_lr_xs[1], y))
            elif self.map_shadow_lr_20_frame == 1:
                surface.blit(self.map_shadow_image_l_20_1, (self.map_shadow_lr_xs[0], y))
                surface.blit(self.map_shadow_image_r_20_1, (self.map_shadow_lr_xs[1], y))
            else:
                surface.blit(self.map_shadow_image_l_20_2, (self.map_shadow_lr_xs[0], y))
                surface.blit(self.map_shadow_image_r_20_2, (self.map_shadow_lr_xs[1], y))

        # now the same things happen for the top 'shadow'
        # change x position in this case
        self.map_shadow_t_xs[0] += self.map_shadow_speed * self.dt
        self.map_shadow_t_xs[1] += self.map_shadow_speed * self.dt

        # move if the images are on the end of the screen
        if self.map_shadow_t_xs[0] > self.render_width:
            self.map_shadow_t_xs[0] -= 512 * 2
        elif self.map_shadow_t_xs[1] > self.render_width:
            self.map_shadow_t_xs[1] -= 512 * 2

        # raise the counter and change the frame if its the time to do so
        self.map_shadow_t_60_count += 1 * self.dt
        if self.map_shadow_t_60_count / 60 >= self.map_shadow_change_speed:
            self.map_shadow_t_60_count = 0
            self.map_shadow_t_60_frame += 1
            if self.map_shadow_t_60_frame >= 3:
                self.map_shadow_t_60_frame = 0

        # same for the other rgb value
        self.map_shadow_t_20_count += 1 * self.dt
        if self.map_shadow_t_20_count / 60 >= self.map_shadow_change_speed:
            self.map_shadow_t_20_count = 0
            self.map_shadow_t_20_frame += 1
            if self.map_shadow_t_20_frame >= 3:
                self.map_shadow_t_20_frame = 0

        # now draw the images relating to the frame
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

        # and same stuff for the bottom 'shadow'
        # move x position
        self.map_shadow_b_xs[0] -= self.map_shadow_speed * self.dt
        self.map_shadow_b_xs[1] -= self.map_shadow_speed * self.dt

        # move image back onto the screen
        if self.map_shadow_b_xs[0] + 512 < 0:
            self.map_shadow_b_xs[0] += 512 * 2
        elif self.map_shadow_b_xs[1] + 512 < 0:
            self.map_shadow_b_xs[1] += 512 * 2

        # change the frame if its time to do so
        if self.map_shadow_b_60_count / 60 >= self.map_shadow_change_speed:
            self.map_shadow_b_60_count = 0
            self.map_shadow_b_60_frame += 1
            if self.map_shadow_b_60_frame >= 3:
                self.map_shadow_b_60_frame = 0
        self.map_shadow_b_60_count += 1 * self.dt

        if self.map_shadow_b_20_count / 60 >= self.map_shadow_change_speed:
            self.map_shadow_b_20_count = 0
            self.map_shadow_b_20_frame += 1
            if self.map_shadow_b_20_frame >= 3:
                self.map_shadow_b_20_frame = 0
        self.map_shadow_b_20_count += 1 * self.dt

        # and finally draw the images by checking the current frame
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

    # create a list that represents the lines for the background
    def make_background_lines(self):
        lines = []
        # the number of lines depends on their height and distance and how many fit onto the screen
        # and two extra lines for the movement
        number_of_lines = round(self.render_height/self.background_lines_distance/2) + 2
        for i in range(number_of_lines):
            y = (i - 2) * (2 * self.background_lines_distance)
            left_point = [0, y]
            right_point = [self.render_width, y + self.background_lines_yoffset]
            # so the lines list contains a list for every line with two more lines in it representing the start and endpoint of the line
            lines.append([left_point, right_point])
        return lines

    # creates the list representing the rects for the background
    def make_background_rects(self):
        rects = []
        for i in range(15):
            # chooses a random size and start rotation and loads the images in the chosen rotation
            size = random.randint(self.background_rects_min_size, self.background_rects_max_size)
            rotation = random.randint(-180, 180)
            image = pygame.transform.scale(self.background_rect_image, (size, size)).convert_alpha()
            shadow_image = pygame.transform.scale(self.background_rect_shadow_image, (size, size)).convert_alpha()

            # sets the position for the rects
            # 3 columns with five rects each
            if i < 5:
                y = (i + 1) * (self.render_height / 3)
                x = self.render_width / 4
            elif i < 10:
                y = (i - 5 + 1.3) * (self.render_height / 3)
                x = (self.render_width / 4) * 2
            else:
                y = (i - 10 + 1.6) * self.render_height / 3
                x = (self.render_width / 4) * 3

            # the rects list contains a list for every rect
            # with the image, the darker image for the shadow effect, the position as a list, the rects size, and its rotation
            rects.append([image, shadow_image, [x, y], size, rotation])
        return rects

    # resets some values and calls reset functions on some of the objects to clear the map etc.
    def prepare_new_round(self):
        self.checked_for_new_highscore = False
        self.new_highscore = False
        self.player.reset(self.player_spawn)
        self.rock_handler.reset()
        self.bullet_handler.reset()
        self.items.clear()

    # checks if the player reached a new highscore
    def check_highscore(self):
        self.checked_for_new_highscore = True
        if self.highscore < self.player.gold_count:
            self.new_highscore = True
            self.game_save['highscore'] = self.player.gold_count
            self.highscore = self.player.gold_count

    # saves the high score and exits the main game loop
    def exit(self):
        # save
        with open('Data/Files/gamesave.json', 'w') as f:
            json.dump(self.game_save, f, indent=4)
        # exit
        self.running = False


# check if if file gets executed or imported
# create game object and run it
if __name__ == '__main__':
    game = Game()
    game.run()
