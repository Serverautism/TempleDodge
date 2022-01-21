import pygame
from random import randint


from . import bullet


# the bullet handler handles the purple projectiles and the bullet phases
class BulletHandler:
    # set attributes
    def __init__(self, default_bullets_per_second, phase_bullets_per_second, phase_time, phase_duration):
        # time between spawning a bullet
        self.default_bullet_time = 60 / default_bullets_per_second
        self.phase_bullet_time = 60 / phase_bullets_per_second

        # attributes for initializing and ending bullet phases
        self.phase_time = phase_time
        self.phase_duration = phase_duration
        self.time_since_last_phase = 0
        self.time_since_last_bullet = 0
        self.phase_count = 0
        self.phase = False

        self.bullets = []

    # main update function
    def update(self, surface, paused):
        if not paused:
            # spawn bullet or activate phase
            # by raising counters and heck if its time to do something
            self.time_since_last_bullet += 1
            self.time_since_last_phase += 1

            # time to start a phase?
            if self.time_since_last_phase / 60 >= self.phase_time:
                self.time_since_last_phase = 0
                self.phase = True

            # check if we need to spawn a bullet based on if we are in a bullet phase or not
            if not self.phase:
                if self.time_since_last_bullet >= self.default_bullet_time:
                    self.time_since_last_bullet = 0
                    self.spawn_bullet()
            else:
                # check if the phase is still going
                self.phase_count += 1
                if self.phase_count / 60 >= self.phase_duration:
                    self.phase = False

                if self.time_since_last_bullet >= self.phase_bullet_time:
                    self.time_since_last_bullet = 0
                    self.spawn_bullet()

        # update the bullets and if they are off screen...
        to_remove = []
        for entity in self.bullets:
            if entity.dead:
                to_remove.append(entity)
            else:
                entity.update(surface, paused)

        # ...remove them
        for entity in to_remove:
            self.bullets.remove(entity)

    # create a new bullet object
    def spawn_bullet(self):
        # walls indexes are representing the walls like this:
        #          1
        #   ____________________
        #   |                  |
        #   |                  |
        # 0 |                  | 2
        #   |                  |
        #   |                  |

        wall_number = randint(0, 2)

        # set the bullets attributes based on the wall the bullet should spawn at
        if wall_number == 0:
            position = [0, randint(16, 272)]
            velocity = [randint(5, 20) / 10, randint(0, 40) / 10 - 2]  # x: from 0,5 to 2  y: from -2 to 2
            while velocity[1] == 0:
                velocity = [randint(5, 20) / 10, randint(0, 40) / 10 - 2]

        elif wall_number == 1:
            position = [randint(16, 496), 0]
            velocity = [randint(0, 40) / 10 - 2, randint(5, 20) / 10]  # x: from -2 to 2  y: from 0,5 to 2
            while velocity[0] == 0:
                velocity = [randint(0, 40) / 10 - 2, randint(5, 20) / 10]

        else:
            position = [512, randint(16, 272)]
            velocity = [randint(5, 20) / -10, randint(0, 40) / 10 - 2]  # x: from -0,5 to -2  y: from -2 to 2
            while velocity[1] == 0:
                velocity = [randint(5, 20) / -10, randint(0, 40) / 10 - 2]

        # add a new bullet object to the list
        self.bullets.append(bullet.Bullet(velocity, position, wall_number))

    # update the particles every bullet if holding
    def update_particles(self, surface):
        for entity in self.bullets:
            entity.update_particles(surface)

    # reset some parameters before starting a new round
    # for example delete all bullets
    def reset(self):
        self.time_since_last_phase = 0
        self.time_since_last_bullet = 0
        self.phase_count = 0
        self.phase = False
        self.bullets.clear()

