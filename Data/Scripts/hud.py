import pygame
from pygame import font


from . import funcs, colors


class Hud:
    def __init__(self, player):
        self.render_width = 512
        self.render_height = 288
        
        self.gold_font_color = colors.gold_font

        self.player = player
        self.mana_position = funcs.grid_pos_to_render_pos((1, 1))[0] - 1, funcs.grid_pos_to_render_pos((1, 1))[1]
        self.font = font.Font('Data/Assets/Font/Font.ttf', 8)
        self.new_highscore_font = font.Font('Data/Assets/Font/Font.ttf', 10)

        self.last_mana_count = self.player.mana_count
        self.last_gold_count = self.player.gold_count

        self.paused_icon = pygame.image.load('Data/Assets/Sprites/Gui/paused_icon.png').convert_alpha()
        self.paused_text = 'press ESCAPE again to unpause'
        self.paused_render = self.render_paused()
        self.paused_render_x = self.render_width / 2 - self.paused_render.get_width() / 2
        self.paused_render_y = self.render_height / 2 - self.paused_render.get_height() / 2

        self.r_icon = pygame.image.load('Data/Assets/Sprites/Gui/r_icon.png')
        self.new_highscore_text = 'NEW HIGHSCORE'
        self.new_highscore_render = self.new_highscore_font.render(self.new_highscore_text, True, colors.font_color)
        self.new_highscore_direction = 'R'
        self.new_highscore_rotation = 0
        self.new_highscore_rotation_change = 2
        self.new_highscore_center = (self.render_width / 2, self.render_height / 2 - 15)

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

        self.render_surface = pygame.Surface((self.render_width, self.render_height))
        self.render_surface.set_colorkey((0, 0, 0))

        self.render_hud(self.last_mana_count, self.last_gold_count)

    def update(self, surface, paused):
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

    def display_dead(self, surface, score, highscore, new_highscore):
        score_text = f'score: {score}, highscore: {highscore}'
        score_text_render = self.font.render(score_text, True, colors.font_color)
        score_text_render_x = self.render_width / 2 - score_text_render.get_width() / 2
        score_text_render_y = self.render_height / 2 - score_text_render.get_height() / 2

        replay_text = 'press R to play again'
        replay_text_render = self.font.render(replay_text, True, colors.font_color)
        r_icon_y = score_text_render_y + 10
        replay_text_render_x = self.render_width / 2 - replay_text_render.get_width() / 2
        r_icon_x = replay_text_render_x - self.r_icon.get_width() - 10
        replay_text_render_y = r_icon_y + self.r_icon.get_height() / 2 - replay_text_render.get_height() / 2

        surface.blit(score_text_render, (score_text_render_x, score_text_render_y))
        surface.blit(replay_text_render, (replay_text_render_x, replay_text_render_y))
        surface.blit(self.r_icon, (r_icon_x, r_icon_y))

        if new_highscore:
            if self.new_highscore_direction == 'R':
                self.new_highscore_rotation += self.new_highscore_rotation_change
                if self.new_highscore_rotation >= 25:
                    self.new_highscore_direction = 'L'
            else:
                self.new_highscore_rotation -= self.new_highscore_rotation_change
                if self.new_highscore_rotation <= -25:
                    self.new_highscore_direction = 'R'

            new_highscore_render = pygame.transform.rotate(self.new_highscore_render, self.new_highscore_rotation)
            new_highscore_render_rect = new_highscore_render.get_rect()
            new_highscore_render_rect.center = self.new_highscore_center

            surface.blit(new_highscore_render, new_highscore_render_rect)

    def display_paused(self, surface):
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
        print('rendered')
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



