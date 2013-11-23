import math

import pygame


class GameObject(object):
    DISPLAY_FLAGS = pygame.SRCALPHA

    def __init__(self, x, y, width, height):
        '''
        x: float, x coordinate in world, range (-1, 1) is on screen
        y: float, y coordinate in world, range (-1, 1) is on screen
        width: float, width in world, scale 1:half_of_display
        height: float, height in world, scale 1:half_of_display
        '''
        self.x = x
        self.y = y
        self.width = width
        self.width_half = width / 2.0
        self.height = height
        self.height_half = height / 2.0
        self.dirty = True

    def draw(self):
        raise NotImplemented

    def render(self, surface):
        display_width = surface.get_width()
        display_height = surface.get_height()
        real_width = display_width * 0.5 * self.width
        real_height = display_height * 0.5 * self.height
        real_x = ((self.x - self.width_half) + 1) * (display_width * 0.5)
        real_y = ((self.y + self.height_half) * -1 + 1) * (display_height * 0.5)
        object_rect = pygame.Rect(real_x, real_y, real_width, real_height)

        # check if this object is off-screen
        if not object_rect.colliderect(surface.get_rect()):
            return

        if self.dirty:
            self.surface = pygame.Surface((real_width, real_height),
                                          GameObject.DISPLAY_FLAGS)
            self.draw()
            self.dirty = False

        surface.blit(self.surface, (real_x, real_y))

    def update(self, delta_time, events):
        raise NotImplemented
