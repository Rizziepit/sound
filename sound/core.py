import math

import pygame


class UpdateableObject(object):
    '''
    Objects that are updated every game loop
    '''

    def update(self, delta_time, events):
        pass


class CollidableObject(object):
    '''
    Objects that are checked for collisions
    '''

    def collide(self, obj):
        pass


class VisibleObject(object):
    '''
    Objects that are rendered every game loop
    '''

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
        self.height = height
        self.dirty = True

    def draw(self):
        pass

    def render(self, surface):
        display_width = surface.get_width()
        display_height = surface.get_height()
        real_width = display_width * 0.5 * self.width
        real_height = display_width * 0.5 * self.height
        real_x = (self.x + 1) * (display_width * 0.5) - (real_width / 2.0)
        real_y = (self.y - 1) * -1 * (display_width * 0.5) - (real_height / 2.0) - (display_width - display_height) / 2.0
        object_rect = pygame.Rect(real_x, real_y, real_width, real_height)

        # check if this object is off-screen
        if not object_rect.colliderect(surface.get_rect()):
            return

        if self.dirty:
            self.surface = pygame.Surface((real_width, real_height),
                                          VisibleObject.DISPLAY_FLAGS)
            self.draw()
            self.dirty = False

        surface.blit(self.surface, (real_x, real_y))


class Pulse(UpdateableObject, CollidableObject, VisibleObject):
    '''
    A pulse that increases it's radius
    over time. Should be removed from
    the game object list once no longer
    visible.
    '''

    def __init__(self, x, y, speed):
        VisibleObject.__init__(self, x, y, 4, 4)
        self.speed = speed
        self.radius = 0.0

    def update(self, delta_time, events):
        self.radius += self.speed * delta_time / 1000.0
        self.dirty = True

    def contains(self, rect):
        # check if all of the four
        # corners are inside the circle
        for x, y in ((rect.left, rect.top),
                     (rect.left, rect.bottom),
                     (rect.right, rect.bottom),
                     (rect.right, rect.top)):
            r2 = (x - self.x)**2 + (y - self.y)**2
            if r2 > self.radius**2:
                return False

        return True

    def draw(self):
        pygame.draw.ellipse(self.surface, (255, 255, 255), pygame.Rect(900-self.radius, 900-self.radius, self.radius*2, self.radius*2))

    def collide(self, obj):
        pass


class HiddenObject(CollidableObject, VisibleObject):

    def __init__(self, x, y, width, height, colour):
        super(HiddenObject, self).__init__(x, y, width, height)
        self.colour = colour

    def draw(self):
        pygame.draw.ellipse(self.surface, self.colour, self.surface.get_rect())

    def collide(self, obj):
        # hidden objects collide with pulses in a special way
        if isinstance(obj, Pulse):
            pass
