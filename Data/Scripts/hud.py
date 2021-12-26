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

        self.last_mana_count = self.player.mana_count
        self.last_gold_count = self.player.gold_count

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

        self.render(self.last_mana_count, self.last_gold_count)

    def update(self, surface):
        # get the counts
        gold = self.player.gold_count
        mana = self.player.mana_count

        if gold != self.last_gold_count or mana != self.last_mana_count:
            self.render(mana, gold)
            self.last_mana_count = mana
            self.last_gold_count = gold

        surface.blit(self.render_surface, (0, 0))

    def render(self, mana, gold):
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



