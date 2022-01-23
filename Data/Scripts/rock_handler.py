import pygame
import random
import copy
import time


from . import rock
from . import chest
from . import funcs


# this object spawns and updates the rocks
class RockHandler:
    # set attributes
    def __init__(self, rocks_per_second):
        self.rock_speed = 1

        # variables for spawning rocks
        self.time_since_last_spawn = 0
        self.rocks_per_second = rocks_per_second
        self.spawn_time = 60 / self.rocks_per_second
        self.time_since_last_wide_spawn = 0
        self.wide_spawn_time = 5
        self.max_column_difference = 4

        # variables for moving rocks for the 'tetris effect'
        self.move_landed_rocks_down = False
        self.pushed_down_counter = 0

        self.falling_rocks = []
        self.landed_rocks = []

        self.chests = []

        # map of landed rock is a list with a list for every column in the 30 x 18 grid
        # with a zero for every empty spot and a 1 for every spot with a rock in it
        self.map_of_landed_rocks = [[0 for _ in range(30)] if j < 17 else [1 for _ in range(30)] for j in range(18)]

        # the column counter is a list with an integer for every column representing the number of rock in each of them
        self.column_counter = [1 for _ in range(30)]

        # available columns holds the index of every column a rock can spawn in
        # while blocked column holds every index of a blocked column with the time it is blocked for
        self.available_columns = [i for i in range(1, 31)]
        self.blocked_columns = []
        self.column_block_time = 16 / self.rock_speed

        # this generates the first line of rocks on the ground of the map
        self.generate_landed_rocks()

        # keeps track of the time between two frames
        self.dt = 0
        self.last_time = time.time()

    # main update function
    def update(self, spawn_rocks, surface, paused):
        # determine delta time since the last frame
        self.dt = time.time() - self.last_time
        self.dt *= 60
        self.last_time = time.time()

        # unblock blocked columns by subtracting the time its blocked for and unblock it if the time is up
        to_remove = []
        for column in self.blocked_columns:
            column[1] -= 1 * self.dt
            if column[1] <= 0:
                # add the index to the available ones
                self.available_columns.append(column[0])
                to_remove.append(column)

        # remove the index from the blocked ones
        for column in to_remove:
            self.blocked_columns.remove(column)

        # spawn rocks if the game is not paused
        if not paused:
            # check if its time so span a rock
            self.time_since_last_spawn += 1 * self.dt
            if spawn_rocks and self.time_since_last_spawn >= self.spawn_time:
                self.time_since_last_spawn = 0

                # get the index of the collum with the smallest amount of rocks
                columns_min_index = self.column_counter.index(min(self.column_counter))

                # choose a random spawn index
                x = random.choice(self.available_columns)

                # block columns that are holding to many rocks
                to_remove = []
                for index in self.available_columns:
                    if self.column_counter[index - 1] > min(self.column_counter) + self.max_column_difference:
                        to_remove.append(index)

                        # if the index chosen spawn was one of them set the spawn to the column with the fewest rocks
                        if index == x:
                            x = columns_min_index + 1

                for index in to_remove:
                    self.available_columns.remove(index)
                    self.blocked_columns.append([index, self.column_block_time])

                # block the finally chosen column
                self.available_columns.remove(x)
                self.blocked_columns.append([x, self.column_block_time])

                # check if its time to spawn a two blocks wide rock
                self.time_since_last_wide_spawn += 1 * self.dt
                if self.time_since_last_wide_spawn >= self.wide_spawn_time:

                    # check if we have the same amount of rock on the left or right side of the chosen spawn to prevent a gap in between the rocks
                    # check the left side
                    if x > 1 and self.column_counter[x - 1] == self.column_counter[x - 2] and x - 1 in self.available_columns:
                        # if it is the same height and column next left from the chosen spawn is not blocked
                        # raise the counter for the columns
                        self.column_counter[x - 2] += 1
                        self.column_counter[x - 1] += 1

                        # set the position of the rock and create a new rock object
                        pos = funcs.grid_pos_to_render_pos((x - 1, -1))
                        new_rock = rock.Rock(pos, self.rock_speed, False, self.landed_rocks, 2)

                        # add the rock to the list
                        self.falling_rocks.append(new_rock)

                        # block the second column
                        self.available_columns.remove(x - 1)
                        self.blocked_columns.append([x - 1, self.column_block_time])

                        # reset the time for the wide block spawn
                        self.time_since_last_wide_spawn = 0

                    # do the same for the right side of the chosen block if left is not possible
                    elif x < 30 and self.column_counter[x - 1] == self.column_counter[x] and x + 1 in self.available_columns:
                        self.column_counter[x - 1] += 1
                        self.column_counter[x] += 1

                        pos = funcs.grid_pos_to_render_pos((x, -1))
                        new_rock = rock.Rock(pos, self.rock_speed, False, self.landed_rocks, 2)

                        self.falling_rocks.append(new_rock)

                        self.available_columns.remove(x + 1)
                        self.blocked_columns.append([x + 1, self.column_block_time])

                        self.time_since_last_wide_spawn = 0

                    # if the left and right side is not possible we just spawn a rock with the width of 1
                    # but we do not reset the timer and retry next time
                    else:
                        # raise the counter for the row the block is in
                        self.column_counter[x - 1] += 1

                        # set the rocks position, create the object and add it to the list
                        pos = funcs.grid_pos_to_render_pos((x, -1))
                        new_rock = rock.Rock(pos, self.rock_speed, False, self.landed_rocks)
                        self.falling_rocks.append(new_rock)

                # if it is not the time to spawn a wider rock
                else:
                    # raise the counter for the row the block is in
                    self.column_counter[x - 1] += 1

                    # set the rocks position, create the object and add it to the list
                    pos = funcs.grid_pos_to_render_pos((x, -1))
                    new_rock = rock.Rock(pos, self.rock_speed, False, self.landed_rocks)
                    self.falling_rocks.append(new_rock)

                # spawn a chest on about every 10th rock
                if random.randint(1, 10) == 1:
                    # create a chest object with a random itm in it on the rock we just spawned
                    self.chests.append(chest.Chest(new_rock, random.choice(['gold', 'mana']), self.landed_rocks, self.falling_rocks))

        # handle the landed rocks
        # if we have to move the landed rocks down...
        if self.move_landed_rocks_down:
            # ...we do that 16 times, 1 pixel per frame
            if self.pushed_down_counter < 16:
                for entity in self.landed_rocks:
                    entity.move_down(1)
                self.pushed_down_counter += 1
            # if we finished moving them down
            else:
                # track that we finished moving them down
                self.move_landed_rocks_down = False
                self.pushed_down_counter = 0

                # move every row in the map of landed rocks down once and...
                for i in range(-1, -len(self.map_of_landed_rocks), -1):
                    self.map_of_landed_rocks[i] = self.map_of_landed_rocks[i - 1].copy()

                # append a empty row on top
                self.map_of_landed_rocks[0] = [0 for _ in range(30)]

                # lower the counter for every column by 1
                for i in range(len(self.column_counter)):
                    self.column_counter[i] -= 1

        # update the landed rocks and remove them if they are off screen
        to_remove = []
        for entity in self.landed_rocks:
            if entity.rect.y > 287:
                to_remove.append(entity)
            else:
                entity.update(surface, paused)

        for entity in to_remove:
            self.landed_rocks.remove(entity)

        # update the falling rocks
        to_move = []
        for entity in self.falling_rocks:
            entity.update(surface, paused)

            # check if they landed
            if entity.landed:
                # add them to the landed rocks later
                to_move.append(entity)

                # translate their position to the position in the grid and set the position to 1 in the map of the landed rocks
                column, column = funcs.render_pos_to_grid_pos((entity.rect.x, entity.rect.y - self.pushed_down_counter))
                self.map_of_landed_rocks[int(column)][int(column) - 1] = 1

                # if the rock if wider, set the position at the right side of the rock to 1 as well
                if entity.width == 2:
                    self.map_of_landed_rocks[int(column)][int(column)] = 1

                # check if the 2 row of rocks from the bottom is 'completed', meaning it is filled with 30 rocks
                if not paused and entity.rect.y == 256:
                    if sum(self.map_of_landed_rocks[-2]) == 30:
                        # if it is save that information to start moving down the landed rocks
                        self.move_landed_rocks_down = True

        # move a landed rock from the falling rocks to the landed rocks list
        for entity in to_move:
            self.falling_rocks.remove(entity)
            self.landed_rocks.append(entity)

    # calls the update particle function on every rock
    def update_particles(self, surface, paused, dead, no_particle_rect):
        for entity in self.falling_rocks + self.landed_rocks:
            entity.update_particles(surface, paused, dead, no_particle_rect)

    # generates the bottom row of rocks at the start of every round
    def generate_landed_rocks(self):
        for i in range(1, 31):
            x, y = funcs.grid_pos_to_render_pos((i, 17))
            self.landed_rocks.append(rock.Rock((x, y), self.rock_speed, True, self.landed_rocks))

    # reset the map before starting a new round
    def reset(self):
        self.time_since_last_spawn = 0
        self.pushed_down_counter = 0
        self.falling_rocks.clear()
        self.landed_rocks.clear()

        self.chests.clear()

        self.map_of_landed_rocks = [[0 for _ in range(30)] if j < 17 else [1 for _ in range(30)] for j in range(18)]
        self.column_counter = [1 for _ in range(30)]

        self.available_columns = [i for i in range(1, 31)]
        self.blocked_columns.clear()

        self.generate_landed_rocks()
