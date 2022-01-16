import pygame
import random
import copy
import time


from . import rock
from . import chest
from . import funcs


class RockHandler:
    def __init__(self, rocks_per_second):
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
        self.time_since_last_wide_spawn = 0
        self.wide_spawn_time = 5
        self.pushed_down_counter = 0
        self.max_collum_difference = 4

        self.falling_rocks = []
        self.landed_rocks = []

        self.chests = []
        self.items = []

        self.map_of_landed_rocks = copy.deepcopy(self.landed_map_default)
        self.row_counter = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
        self.available_rows = list(range(1, 31))
        self.blocked_rows = []
        self.row_block_time = 16 / self.rock_speed

        self.generate_landed_rocks()

        self.dt = 0
        self.last_time = time.time()

    def update(self, spawn_rocks, surface, paused):
        # determine delta time
        self.dt = time.time() - self.last_time
        self.dt *= 60
        self.last_time = time.time()
        # unblock blocked collums
        to_remove = []
        for row in self.blocked_rows:
            row[1] -= 1 * self.dt
            if row[1] <= 0:
                self.available_rows.append(row[0])
                to_remove.append(row)

        for row in to_remove:
            self.blocked_rows.remove(row)

        # spawn rocks
        if not paused:
            self.time_since_last_spawn += 1 * self.dt
            if spawn_rocks and self.time_since_last_spawn >= self.spawn_time:
                self.time_since_last_spawn = 0
                rows_min_index = self.row_counter.index(min(self.row_counter))

                # choose a spawn
                x = random.choice(self.available_rows)

                # block rows that are to high
                to_remove = []
                for index in self.available_rows:
                    if self.row_counter[index - 1] > min(self.row_counter) + self.max_collum_difference:
                        to_remove.append(index)
                        if index == x:
                            x = rows_min_index + 1

                for index in to_remove:
                    self.available_rows.remove(index)
                    self.blocked_rows.append([index, self.row_block_time])

                # block spawn
                self.available_rows.remove(x)
                self.blocked_rows.append([x, self.row_block_time])

                # spawn wide rock
                self.time_since_last_wide_spawn += 1 * self.dt
                if self.time_since_last_wide_spawn >= self.wide_spawn_time:

                    # if left from spawn is same hight
                    if x > 1 and self.row_counter[x - 1] == self.row_counter[x - 2] and x - 1 in self.available_rows:
                        self.row_counter[x - 2] += 1
                        self.row_counter[x - 1] += 1

                        pos = funcs.grid_pos_to_render_pos((x - 1, -1))
                        new_rock = rock.Rock(pos, self.rock_speed, False, 2)

                        self.falling_rocks.append(new_rock)

                        self.available_rows.remove(x - 1)
                        self.blocked_rows.append([x - 1, self.row_block_time])

                        self.time_since_last_wide_spawn = 0

                    # if right from spawn is same hight
                    elif x < 30 and self.row_counter[x - 1] == self.row_counter[x] and x + 1 in self.available_rows:
                        self.row_counter[x - 1] += 1
                        self.row_counter[x] += 1

                        pos = funcs.grid_pos_to_render_pos((x, -1))
                        new_rock = rock.Rock(pos, self.rock_speed, False, 2)

                        self.falling_rocks.append(new_rock)

                        self.available_rows.remove(x + 1)
                        self.blocked_rows.append([x + 1, self.row_block_time])

                        self.time_since_last_wide_spawn = 0

                    else:
                        self.row_counter[x - 1] += 1

                        pos = funcs.grid_pos_to_render_pos((x, -1))
                        new_rock = rock.Rock(pos, self.rock_speed, False)

                        self.falling_rocks.append(new_rock)

                else:
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

                if entity.width == 2:
                    self.map_of_landed_rocks[int(row)][int(collum)] = 1

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
