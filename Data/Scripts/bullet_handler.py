import pygame
from random import randint


from . import bullet


class BulletHandler:
    def __init__(self, default_bullets_per_second, phase_bullets_per_second, phase_time, phase_duration):
        self.default_bullet_time = 60 / default_bullets_per_second
        self.phase_bullet_time = 60 / phase_bullets_per_second
        self.phase_time = phase_time
        self.phase_duration = phase_duration
        self.time_since_last_phase = 0
        self.time_since_last_bullet = 0
        self.phase_count = 0
        self.phase = False

        self.bullets = []

    def update(self, surface, paused):
        if not paused:
            # spawn bullet or activate phase
            self.time_since_last_bullet += 1
            self.time_since_last_phase += 1

            if self.time_since_last_phase / 60 >= self.phase_time:
                self.time_since_last_phase = 0
                self.phase = True

            if not self.phase:
                if self.time_since_last_bullet >= self.default_bullet_time:
                    self.time_since_last_bullet = 0
                    self.spawn_bullet()
            else:
                self.phase_count += 1
                if self.phase_count / 60 >= self.phase_duration:
                    self.phase = False

                if self.time_since_last_bullet >= self.phase_bullet_time:
                    self.time_since_last_bullet = 0
                    self.spawn_bullet()

        to_remove = []
        for entity in self.bullets:
            if entity.dead:
                to_remove.append(entity)
            else:
                entity.update(surface, paused)

        for entity in to_remove:
            self.bullets.remove(entity)

    def spawn_bullet(self):
        # walls:
        #          1
        #   ____________________
        #   |                  |
        #   |                  |
        # 0 |                  | 2
        #   |                  |
        #   |                  |

        wall_number = randint(0, 2)

        if wall_number == 0:
            position = [0, randint(16, 272)]
            velocity = [randint(5, 20) / 10, randint(0, 40) / 10 - 2]  # x: from 0,5 to 2  y: from -2 to 2
            while velocity[0] == 0 or velocity[1] == 0:
                velocity = [randint(5, 20) / 10, randint(0, 40) / 10 - 2]

        elif wall_number == 1:
            position = [randint(16, 496), 0]
            velocity = [randint(0, 40) / 10 - 2, randint(5, 20) / 10]  # x: from -2 to 2  y: from 0,5 to 2
            while velocity[0] == 0 or velocity[1] == 0:
                velocity = [randint(0, 40) / 10 - 2, randint(5, 20) / 10]

        else:
            position = [512, randint(16, 272)]
            velocity = [randint(5, 20) / -10, randint(0, 40) / 10 - 2]  # x: from -0,5 to -2  y: from -2 to 2
            while velocity[0] == 0 or velocity[1] == 0:
                velocity = [randint(5, 20) / -10, randint(0, 40) / 10 - 2]

        self.bullets.append(bullet.Bullet(velocity, position))

    def reset(self):
        self.time_since_last_phase = 0
        self.time_since_last_bullet = 0
        self.phase_count = 0
        self.phase = False
        self.bullets.clear()

