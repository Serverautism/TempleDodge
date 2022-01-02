import pygame


class Particle:
    def __init__(self, center, velocity, radius, lifetime, color, glow_color, static_size=False, has_glow=False, rocks=None,
                 gravity=0, glow_scale=5):
        self.center = center
        self.velocity = velocity
        self.radius = radius
        self.lifetime = lifetime * 60
        self.color = color
        self.glow_color = glow_color
        self.static_size = static_size
        self.has_glow = has_glow
        self.rock = rocks
        self.gravity = gravity
        self.glow_scale = glow_scale

        self.dead = False

        if self.static_size and self.has_glow:
            self.glow_image = self.get_glow()
        elif not self.static_size:
            self.radius_change = .1

    def update(self, surface):
        # change position
        self.center[0] += self.velocity[0]
        self.center[1] += self.velocity[1]

        # interact with rocks

        # apply gravity
        self.velocity[1] += self.gravity

        # change radius
        if not self.static_size:
            self.radius -= self.radius_change
            if self.radius <= 0:
                self.dead = True
                return
        else:
            self.lifetime -= 1
            if self.lifetime <= 0:
                self.dead = True

        # draw glow
        if self.has_glow:
            if self.static_size:
                surface.blit(self.glow_image, (int(self.center[0]) - int(self.radius * self.glow_scale), int(self.center[1]) - int(self.radius * self.glow_scale)), special_flags=pygame.BLEND_RGB_ADD)
            else:
                surface.blit(self.get_glow(), (int(self.center[0]) - int(self.radius * self.glow_scale), int(self.center[1]) - int(self.radius * self.glow_scale)), special_flags=pygame.BLEND_RGB_ADD)

        # draw particle
        pygame.draw.circle(surface, self.color, [int(self.center[0]), int(self.center[1])], int(self.radius))

    def get_glow(self):
        glow_radius = int(self.radius * self.glow_scale)
        surface = pygame.Surface((glow_radius * 2, glow_radius * 2)).convert_alpha()
        surface.set_colorkey((0, 0, 0))
        pygame.draw.circle(surface, self.glow_color, (glow_radius, glow_radius), glow_radius)
        return surface

    def get_glow_color(self):
        r, g, b = self.color
        min_val = min([i for i in self.color if i > 0])
        diff = 20 - min_val
        if diff < 0:
            return r - abs(diff), g - abs(diff), b - abs(diff)
        else:
            return self.color
