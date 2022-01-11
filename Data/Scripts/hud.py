import pygame
from pygame import font
import time


from . import funcs, colors


class Hud:
    def __init__(self, player):
        self.render_width = 512
        self.render_height = 288
        
        self.gold_font_color = colors.gold_font

        self.player = player
        self.mana_position = funcs.grid_pos_to_render_pos((1, 1))[0] - 1, funcs.grid_pos_to_render_pos((1, 1))[1]
        self.font = font.Font('Data/Assets/Font/Font.ttf', 8)
        self.new_highscore_font = font.Font('Data/Assets/Font/Font.ttf', 15)

        self.last_mana_count = self.player.mana_count
        self.last_gold_count = self.player.gold_count

        self.paused_icon = pygame.image.load('Data/Assets/Sprites/Gui/paused_icon.png').convert_alpha()
        self.paused_text = 'press ESCAPE to resume'
        self.paused_render = self.render_paused()
        self.paused_render_x = self.render_width / 2 - self.paused_render.get_width() / 2
        self.paused_render_y = self.render_height / 2 - self.paused_render.get_height() / 2

        self.r_icon = pygame.image.load('Data/Assets/Sprites/Gui/r_icon.png')
        self.new_highscore_text = 'NEW HIGHSCORE'
        self.new_highscore_render = self.new_highscore_font.render(self.new_highscore_text, True, colors.font_color)
        self.new_highscore_direction = 'R'
        self.new_highscore_rotation = 0
        self.new_highscore_rotation_change = 2
        self.new_highscore_rotation_max = 10
        self.new_highscore_center = (self.render_width / 2, self.render_height / 2 - 25)

        self.score_text_render = None
        self.replay_text_render = None
        self.score_text_render_x = 0
        self.score_text_render_y = 0
        self.r_icon_x = 0
        self.r_icon_y = 0
        self.replay_text_render_x = 0
        self.replay_text_render_y = 0

        self.mana_frame = pygame.image.load('Data/Assets/Sprites/Gui/frame_mana.png').convert_alpha()
        self.mana_frame_rect = self.mana_frame.get_rect()
        self.mana_frame_rect.x, self.mana_frame_rect.y = self.mana_position

        self.gold_frame = pygame.image.load('Data/Assets/Sprites/Gui/frame_gold.png').convert_alpha()
        self.gold_frame_rect = self.gold_frame.get_rect()
        self.gold_frame_rect.x = self.mana_position[0]
        self.gold_frame_rect.y = self.mana_position[1] + self.mana_frame_rect[3]

        self.mana_bar_lightblue_frames = []
        self.mana_bar_darkblue_frames = []

        for i in range(2):
            image = pygame.image.load(f'Data/Assets/Sprites/Gui/bar_mana_darkblue_{i + 1}.png').convert_alpha()
            self.mana_bar_darkblue_frames.append(image)

        self.text_background_frame = 0
        self.text_background_change = 0.1
        self.text_background_count = 0
        self.text_background_length = 6
        self.text_background_30_frames = []
        self.text_background_20_frames = []

        for i in range(self.text_background_length):
            image = pygame.image.load(f'Data/Assets/Sprites/Gui/gui_background_30_{i + 1}.png').convert_alpha()
            self.text_background_30_frames.append(image)
            image = pygame.image.load(f'Data/Assets/Sprites/Gui/gui_background_20_{i + 1}.png').convert_alpha()
            self.text_background_20_frames.append(image)

        self.render_surface = pygame.Surface((self.render_width, self.render_height))
        self.render_surface.set_colorkey((0, 0, 0))

        self.render_hud(self.last_mana_count, self.last_gold_count)

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

        if gold != self.last_gold_count or mana != self.last_mana_count:
            self.render_hud(mana, gold)
            self.last_mana_count = mana
            self.last_gold_count = gold

        surface.blit(self.render_surface, (0, 0))

        if paused:
            self.display_paused(surface)

    def display_dead(self, surface, new_highscore):
        self.draw_text_background(surface)

        surface.blit(self.score_text_render, (self.score_text_render_x, self.score_text_render_y))
        surface.blit(self.replay_text_render, (self.replay_text_render_x, self.replay_text_render_y))
        surface.blit(self.r_icon, (self.r_icon_x, self.r_icon_y))

        if new_highscore:
            if self.new_highscore_direction == 'R':
                self.new_highscore_rotation += self.new_highscore_rotation_change * self.dt
                if self.new_highscore_rotation >= self.new_highscore_rotation_max:
                    self.new_highscore_direction = 'L'
            else:
                self.new_highscore_rotation -= self.new_highscore_rotation_change * self.dt
                if self.new_highscore_rotation <= -self.new_highscore_rotation_max:
                    self.new_highscore_direction = 'R'

            new_highscore_render = pygame.transform.rotate(self.new_highscore_render, self.new_highscore_rotation)
            new_highscore_render_rect = new_highscore_render.get_rect()
            new_highscore_render_rect.center = self.new_highscore_center

            surface.blit(new_highscore_render, new_highscore_render_rect)
    
    def render_dead(self, score, highscore):
        score_text = f'score: {score}, highscore: {highscore}'
        self.score_text_render = self.font.render(score_text, True, colors.font_color)
        self.score_text_render_x = self.render_width / 2 - self.score_text_render.get_width() / 2
        self.score_text_render_y = self.render_height / 2 - self.score_text_render.get_height() / 2

        replay_text = 'press R to play again'
        self.replay_text_render = self.font.render(replay_text, True, colors.font_color)
        self.r_icon_y = self.score_text_render_y + 10
        self.replay_text_render_x = self.render_width / 2 - self.replay_text_render.get_width() / 2
        self.r_icon_x = self.replay_text_render_x - self.r_icon.get_width() - 10
        self.replay_text_render_y = self.r_icon_y + self.r_icon.get_height() / 2 - self.replay_text_render.get_height() / 2

    def draw_text_background(self, surface):
        self.text_background_count += 1 * self.dt
        if self.text_background_count / 60 >= self.text_background_change:
            self.text_background_count = 0
            self.text_background_frame += 1
            if self.text_background_frame == self.text_background_length:
                self.text_background_frame = 0

        surface.blit(self.text_background_30_frames[self.text_background_frame], (-10, 10),
                     special_flags=pygame.BLEND_RGB_SUB)
        surface.blit(self.text_background_20_frames[self.text_background_frame], (0, 0))

    def display_paused(self, surface):
        self.draw_text_background(surface)

        surface.blit(self.paused_render, (self.paused_render_x, self.paused_render_y))

    def render_paused(self):
        textrender = self.font.render(self.paused_text, True, colors.font_color)

        width = textrender.get_width() + self.paused_icon.get_width() + 10
        height = self.paused_icon.get_height()
        render_surface = pygame.Surface((width, height))
        render_surface.set_colorkey((0, 0, 0))

        render_surface.blit(self.paused_icon, (0, 0))
        render_surface.blit(textrender, (self.paused_icon.get_width() + 10, 5))

        return render_surface

    def render_hud(self, mana, gold):
        self.render_surface.fill((0, 0, 0))
        # draw the frames
        self.render_surface.blit(self.mana_frame, self.mana_frame_rect)
        self.render_surface.blit(self.gold_frame, self.gold_frame_rect)
        # draw mana bar
        for i in range(mana):
            position = (self.mana_position[0] + i * 8 + 1, self.mana_position[1])

            if i == mana - 1:
                self.render_surface.blit(self.mana_bar_darkblue_frames[1], position)
            else:
                self.render_surface.blit(self.mana_bar_darkblue_frames[0], position)
        # render gold number
        gold_count_render = self.font.render(str(gold), False, self.gold_font_color)
        gold_count_render_rect = gold_count_render.get_rect()
        gold_count_render_rect.top = self.gold_frame_rect.top + 4
        gold_count_render_rect.right = self.gold_frame_rect.right - 3
        self.render_surface.blit(gold_count_render, gold_count_render_rect)



