import pygame
from pygame import font
import time


from . import funcs, colors


# this object displays the counters for gold and mana
# as well as the messages on the center of the screen
class Hud:
    # first set attributes
    def __init__(self, player):
        self.render_width = 512
        self.render_height = 288

        # if the game just got started
        self.first_time = True
        
        self.gold_font_color = colors.gold_font

        # get the player object to update the counters
        self.player = player

        self.mana_position = funcs.grid_pos_to_render_pos((1, 1))[0] - 1, funcs.grid_pos_to_render_pos((1, 1))[1]

        # load the fonts for the text
        self.font = font.Font('Data/Assets/Font/Font.ttf', 8)
        self.new_highscore_font = font.Font('Data/Assets/Font/Font.ttf', 15)

        # gte the counts
        self.last_mana_count = self.player.mana_count
        self.last_gold_count = self.player.gold_count

        # set some variables for the start game message
        self.startup_text = 'press SPACE to play'
        self.space_icon = pygame.image.load('Data/Assets/Sprites/Gui/space_icon.png').convert_alpha()
        self.startup_render = self.render_startup()
        self.startup_render_x = self.render_width / 2 - self.startup_render.get_width() / 2
        self.startup_render_y = self.render_height / 2 - self.startup_render.get_height() / 2

        # set some variables for the game paused message
        self.paused_icon = pygame.image.load('Data/Assets/Sprites/Gui/paused_icon.png').convert_alpha()
        self.paused_text = 'press ESCAPE to resume'
        self.paused_render = self.render_paused()
        self.paused_render_x = self.render_width / 2 - self.paused_render.get_width() / 2
        self.paused_render_y = self.render_height / 2 - self.paused_render.get_height() / 2

        # same for the game over message
        self.r_icon = pygame.image.load('Data/Assets/Sprites/Gui/r_icon.png')
        self.new_highscore_text = 'NEW HIGHSCORE'
        self.replay_text = 'press R to play again'
        self.new_highscore_render = self.new_highscore_font.render(self.new_highscore_text, True, colors.font_color)
        self.new_highscore_direction = 'R'
        self.new_highscore_rotation = 0
        self.new_highscore_rotation_change = 2
        self.new_highscore_rotation_max = 10
        self.new_highscore_center = (self.render_width / 2, self.render_height / 2 - 25)

        # variables to apply values when rendering a message
        self.score_text_render = None
        self.replay_text_render = None
        self.score_text_render_x = 0
        self.score_text_render_y = 0
        self.r_icon_x = 0
        self.r_icon_y = 0
        self.replay_text_render_x = 0
        self.replay_text_render_y = 0

        # load images for the mana bar and set the render position
        self.mana_frame = pygame.image.load('Data/Assets/Sprites/Gui/frame_mana.png').convert_alpha()
        self.mana_frame_rect = self.mana_frame.get_rect()
        self.mana_frame_rect.x, self.mana_frame_rect.y = self.mana_position

        # same for the gold counter
        self.gold_frame = pygame.image.load('Data/Assets/Sprites/Gui/frame_gold.png').convert_alpha()
        self.gold_frame_rect = self.gold_frame.get_rect()
        self.gold_frame_rect.x = self.mana_position[0]
        self.gold_frame_rect.y = self.mana_position[1] + self.mana_frame_rect[3]

        # load the parts of the blue mana bar into lists
        self.mana_bar_lightblue_frames = []
        self.mana_bar_darkblue_frames = []

        for i in range(2):
            image = pygame.image.load(f'Data/Assets/Sprites/Gui/bar_mana_darkblue_{i + 1}.png').convert_alpha()
            self.mana_bar_darkblue_frames.append(image)

        # set variables for the moving 'shadow' type message background
        self.text_background_frame = 0
        self.text_background_change = 0.1
        self.text_background_count = 0
        self.text_background_length = 6

        # and load its animation frames into lists
        self.text_background_30_frames = []
        self.text_background_20_frames = []

        for i in range(self.text_background_length):
            image = pygame.image.load(f'Data/Assets/Sprites/Gui/gui_background_30_{i + 1}.png').convert_alpha()
            self.text_background_30_frames.append(image)
            image = pygame.image.load(f'Data/Assets/Sprites/Gui/gui_background_20_{i + 1}.png').convert_alpha()
            self.text_background_20_frames.append(image)

        # create a new render surface
        self.render_surface = pygame.Surface((100, 100))
        self.render_surface.set_colorkey((0, 0, 0))

        # and draw the counts on it
        self.render_hud(self.last_mana_count, self.last_gold_count)

        # track the time between frames
        self.dt = 0
        self.last_time = time.time()

    def update(self, surface, paused):
        # calc delta time
        self.dt = time.time() - self.last_time
        self.dt *= 60
        self.last_time = time.time()

        # get the counts
        gold = self.player.gold_count
        mana = self.player.mana_count

        # if the counts changes we make a new render of the counts
        if gold != self.last_gold_count or mana != self.last_mana_count:
            self.render_hud(mana, gold)
            self.last_mana_count = mana
            self.last_gold_count = gold

        # draw the counts
        surface.blit(self.render_surface, (0, 0))

        # if the game is paused display a message depending on if we just started the game or not
        if paused:
            if self.first_time:
                self.display_startup(surface)
            else:
                self.display_paused(surface)

    # displays the game over message
    def display_dead(self, surface, new_highscore):
        # first draw the text background 'shadow' cloud thing
        self.draw_text_background(surface)

        # then draw the text and the icon for the r key on it
        surface.blit(self.score_text_render, (self.score_text_render_x, self.score_text_render_y))
        surface.blit(self.replay_text_render, (self.replay_text_render_x, self.replay_text_render_y))
        surface.blit(self.r_icon, (self.r_icon_x, self.r_icon_y))

        # if the player reached a new high score
        # draw the text and rotate it every few frames
        if new_highscore:
            # rotate it left or right
            if self.new_highscore_direction == 'R':
                self.new_highscore_rotation += self.new_highscore_rotation_change * self.dt
                if self.new_highscore_rotation >= self.new_highscore_rotation_max:
                    self.new_highscore_direction = 'L'
            else:
                self.new_highscore_rotation -= self.new_highscore_rotation_change * self.dt
                if self.new_highscore_rotation <= -self.new_highscore_rotation_max:
                    self.new_highscore_direction = 'R'

            # render the text based on the rotation and set its position based on the size of the render
            new_highscore_render = pygame.transform.rotate(self.new_highscore_render, self.new_highscore_rotation)
            new_highscore_render_rect = new_highscore_render.get_rect()
            new_highscore_render_rect.center = self.new_highscore_center

            # draw it
            surface.blit(new_highscore_render, new_highscore_render_rect)

    # pre render the texts for the game over message
    # gets called after the player dies
    def render_dead(self, score, highscore):
        # create the text based on the score and high score the player reached
        score_text = f'score: {score}, highscore: {highscore}'

        # render the text and set its render position based on the size of the render
        self.score_text_render = self.font.render(score_text, True, colors.font_color)
        self.score_text_render_x = self.render_width / 2 - self.score_text_render.get_width() / 2
        self.score_text_render_y = self.render_height / 2 - self.score_text_render.get_height() / 2

        # do the same for the replay text and set its position and the r key icons position based on the render size of the text
        self.replay_text_render = self.font.render(self.replay_text, True, colors.font_color)
        self.r_icon_y = self.score_text_render_y + 10
        self.replay_text_render_x = self.render_width / 2 - self.replay_text_render.get_width() / 2
        self.r_icon_x = self.replay_text_render_x - self.r_icon.get_width() - 10
        self.replay_text_render_y = self.r_icon_y + self.r_icon.get_height() / 2 - self.replay_text_render.get_height() / 2

    # this function draws the background for the hud messages
    def draw_text_background(self, surface):
        # check if its time to go to the next frame and if it is do so
        self.text_background_count += 1 * self.dt
        if self.text_background_count / 60 >= self.text_background_change:
            self.text_background_count = 0
            self.text_background_frame += 1

            # reset to the first frame if the animation finished
            if self.text_background_frame == self.text_background_length:
                self.text_background_frame = 0

        # draw the transparent layer first, than the solid one
        surface.blit(self.text_background_30_frames[self.text_background_frame], (-10, 10), special_flags=pygame.BLEND_RGB_SUB)
        surface.blit(self.text_background_20_frames[self.text_background_frame], (0, 0))

    # this function draws the paused message
    def display_paused(self, surface):
        # draw the text background
        self.draw_text_background(surface)

        # draw the pre rendered text on top
        surface.blit(self.paused_render, (self.paused_render_x, self.paused_render_y))

    # this function pre renders the text for the paused message
    def render_paused(self):
        # render the text
        textrender = self.font.render(self.paused_text, True, colors.font_color)

        # create a new surface based on the text render dimensions
        width = textrender.get_width() + self.paused_icon.get_width() + 10
        height = self.paused_icon.get_height()
        render_surface = pygame.Surface((width, height))
        render_surface.set_colorkey((0, 0, 0))

        # draw the r key icon and the text onto the new surface
        render_surface.blit(self.paused_icon, (0, 0))
        render_surface.blit(textrender, (self.paused_icon.get_width() + 10, 5))

        return render_surface

    # this displays the startup message at the beginning of the game
    def display_startup(self, surface):
        self.draw_text_background(surface)

        surface.blit(self.startup_render, (self.startup_render_x, self.startup_render_y))

    # this function pre renders ht startup message
    def render_startup(self):
        # render the text
        textrender = self.font.render(self.startup_text, True, colors.font_color)

        # create a new surface based on the text render dimensions
        width = textrender.get_width() + self.space_icon.get_width() + 10
        height = self.space_icon.get_height()
        render_surface = pygame.Surface((width, height))
        render_surface.set_colorkey((0, 0, 0))

        # draw the SPACE key icon and the text onto the new surface
        render_surface.blit(self.space_icon, (0, 0))
        render_surface.blit(textrender, (self.space_icon.get_width() + 10, 5))

        return render_surface

    # renders the counts
    def render_hud(self, mana, gold):
        # fills the surface to clear it
        self.render_surface.fill((0, 0, 0))

        # draw the frames as the background for the bar and the gold count
        self.render_surface.blit(self.mana_frame, self.mana_frame_rect)
        self.render_surface.blit(self.gold_frame, self.gold_frame_rect)

        # draws the mana bar based on the amount of mana the player collected
        for i in range(mana):
            # calculate the position for the next part of the bar
            position = (self.mana_position[0] + i * 8 + 1, self.mana_position[1])

            # draws a middle or end part ot the blue bar
            if i == mana - 1:
                self.render_surface.blit(self.mana_bar_darkblue_frames[1], position)
            else:
                self.render_surface.blit(self.mana_bar_darkblue_frames[0], position)

        # render gold number and set its position based on the size of the render
        gold_count_render = self.font.render(str(gold), False, self.gold_font_color)
        gold_count_render_rect = gold_count_render.get_rect()
        gold_count_render_rect.top = self.gold_frame_rect.top + 4
        gold_count_render_rect.right = self.gold_frame_rect.right - 3

        # draws the number for the gold counter onto the surface
        self.render_surface.blit(gold_count_render, gold_count_render_rect)



