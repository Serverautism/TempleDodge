import pygame
import time


# this object represents one of the particles used by many objects in the game
class Particle:
    def __init__(self, center, velocity, radius, lifetime, color, glow_color, static_size=False, has_glow=False, rocks=None, gravity=0, glow_scale=5):
        self.center = center
        self.velocity = velocity
        self.radius = radius

        # lifetime is the duration before the particle dies
        self.lifetime = lifetime * 60

        self.color = color
        self.glow_color = glow_color

        # does the particle keeps its size over its lifetime?
        self.static_size = static_size

        self.has_glow = has_glow

        # used for physics if the particle has them enabled
        self.rock = rocks

        self.gravity = gravity

        # size of the glow compared to the radius of the particle
        self.glow_scale = glow_scale

        self.dead = False

        # track them time since the last frame
        self.last_time = time.time()
        self.dt = 0

        # if the particle does not change its size we pre render the glow image
        if self.static_size and self.has_glow:
            self.glow_image = self.get_glow()

        # else if the particle changes size over time we calculate the change per frame
        # so that its size is 0 when it dies
        elif not self.static_size:
            self.radius_change = self.radius / self.lifetime

    # main update function
    def update(self, surface):
        # calculate the delta time since the last frame
        self.dt = time.time() - self.last_time
        self.dt *= 60
        self.last_time = time.time()

        # change position based on velocity and the time passed
        self.center[0] += self.velocity[0] * self.dt
        self.center[1] += self.velocity[1] * self.dt

        # interact with rocks

        # apply gravity to the movement on the y-axis
        self.velocity[1] += self.gravity * self.dt

        # change radius if the particle is not static in its size
        if not self.static_size:
            self.radius -= self.radius_change * self.dt
            if self.radius <= 0:
                self.dead = True
                return

        # otherwise we just count down the lifetime
        else:
            self.lifetime -= 1 * self.dt
            if self.lifetime <= 0:
                self.dead = True

        # if the particle has glow enabled
        if self.has_glow:
            # we draw the pre rendered image for static sizes
            if self.static_size:
                surface.blit(self.glow_image, (int(self.center[0]) - int(self.radius * self.glow_scale), int(self.center[1]) - int(self.radius * self.glow_scale)), special_flags=pygame.BLEND_RGB_ADD)

            # or generate a new glow image with the changed radius
            else:
                surface.blit(self.get_glow(), (int(self.center[0]) - int(self.radius * self.glow_scale), int(self.center[1]) - int(self.radius * self.glow_scale)), special_flags=pygame.BLEND_RGB_ADD)

        # draw the particle
        pygame.draw.circle(surface, self.color, [int(self.center[0]), int(self.center[1])], int(self.radius))

    # renders the glow
    def get_glow(self):
        # calculate the radius of the glow
        glow_radius = int(self.radius * self.glow_scale)

        # create a new surface to draw the radius on
        surface = pygame.Surface((glow_radius * 2, glow_radius * 2)).convert_alpha()
        surface.set_colorkey((0, 0, 0))

        # then draw the glow as a circle onto the new surface
        pygame.draw.circle(surface, self.glow_color, (glow_radius, glow_radius), glow_radius)

        return surface
