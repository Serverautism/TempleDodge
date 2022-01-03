import pygame
import random
import copy

from . import rock
from . import chest
from . import funcs


class RockHandler:
    def __init__(self, rocks_per_second, rocks_per_second_change):
        self.landed_map_default = [
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
        ]

        self.rock_speed = 1
        self.time_since_last_spawn = 0
        self.rocks_per_second = rocks_per_second
        self.spawn_time = 60 / self.rocks_per_second
        self.pushed_down_counter = 0
        self.max_collum_difference = 4

        self.falling_rocks = []
        self.landed_rocks = []

        self.chests = []
        self.items = []

        self.map_of_landed_rocks = copy.deepcopy(self.landed_map_default)
        self.row_counter = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]

        self.generate_landed_rocks()

    def update(self, spawn_rocks, surface, paused):
        # spawn rocks
        if not paused:
            self.time_since_last_spawn += 1
            if spawn_rocks and self.time_since_last_spawn >= self.spawn_time:
                rows_min_index = self.row_counter.index(min(self.row_counter))
                self.time_since_last_spawn = 0
                x = random.randint(1, 30)
                if self.row_counter[x - 1] > min(self.row_counter) + self.max_collum_difference:
                    x = rows_min_index + 1
                self.row_counter[x - 1] += 1
                pos = funcs.grid_pos_to_render_pos((x, -1))
                new_rock = rock.Rock(pos, self.rock_speed, False)
                self.falling_rocks.append(new_rock)
                # spawn chest
                if random.randint(1, 10) == 1:
                    self.chests.append(chest.Chest(new_rock, random.choice(['gold', 'mana']), self.landed_rocks, self.falling_rocks))

        # handle landed rocks
        to_remove = []
        for entity in self.landed_rocks:
            entity.update(surface, paused)
            if entity.rect.y > 288:
                to_remove.append(entity)

        for entity in to_remove:
            self.landed_rocks.remove(entity)

        # handle falling rocks
        to_move = []
        for entity in self.falling_rocks:
            entity.update(surface, paused, self.landed_rocks)
            if entity.landed:
                to_move.append(entity)
                collum, row = funcs.render_pos_to_grid_pos((entity.rect.x, entity.rect.y - self.pushed_down_counter))
                self.map_of_landed_rocks[int(row)][int(collum) - 1] = 1

        for entity in to_move:
            self.falling_rocks.remove(entity)
            self.landed_rocks.append(entity)

        # tetris check
        if not paused:
            if sum(self.map_of_landed_rocks[-2][:30]) == 30:
                if self.pushed_down_counter < 16:
                    for entity in self.landed_rocks:
                        entity.move_down(1)
                    self.pushed_down_counter += 1
                else:
                    self.pushed_down_counter = 0
                    for i in range(-1, -len(self.map_of_landed_rocks), -1):
                        self.map_of_landed_rocks[i] = self.map_of_landed_rocks[i - 1].copy()
                    self.map_of_landed_rocks[0] = self.landed_map_default[0].copy()
                    for i in range(len(self.row_counter)):
                        self.row_counter[i] -= 1

    def update_particles(self, surface):
        for entity in self.falling_rocks + self.landed_rocks:
            entity.update_particles(surface)

    def generate_landed_rocks(self):
        for i in range(1, 31):
            x, y = funcs.grid_pos_to_render_pos((i, 17))
            self.landed_rocks.append(rock.Rock((x, y), self.rock_speed, True))

    def reset(self):
        self.time_since_last_spawn = 0
        self.pushed_down_counter = 0
        self.falling_rocks.clear()
        self.landed_rocks.clear()

        self.chests.clear()
        self.items.clear()

        self.map_of_landed_rocks = copy.deepcopy(self.landed_map_default)
        self.row_counter = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]

        self.generate_landed_rocks()
