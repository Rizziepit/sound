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
        self.visible = True

    def draw(self):
        pass

    def render(self, surface):
        if not self.visible:
            return

        display_width = surface.get_width()
        display_height = surface.get_height()
        self.real_width = display_width * 0.5 * self.width
        self.real_height = display_width * 0.5 * self.height
        self.real_x = (self.x + 1) * (display_width * 0.5) - (self.real_width / 2.0)
        self.real_y = ((self.y - 1) * -1 * (display_width * 0.5)
                       - (self.real_height / 2.0)
                       - (display_width - display_height) / 2.0)
        object_rect = pygame.Rect(self.real_x, self.real_y,
                                  self.real_width, self.real_height)

        # check if this object is off-screen
        if not object_rect.colliderect(surface.get_rect()):
            return

        if self.dirty:
            self.surface = pygame.Surface((self.real_width, self.real_height),
                                          VisibleObject.DISPLAY_FLAGS)
            self.draw()
            self.dirty = False

        surface.blit(self.surface, (self.real_x, self.real_y))


class Pulse(UpdateableObject, CollidableObject, VisibleObject):
    '''
    A pulse that increases it's radius
    over time.
    '''

    def __init__(self, x, y, speed):
        VisibleObject.__init__(self, x, y, 4, 4)
        self.speed = speed
        self.radius = 0.0
        self.visible = False

    def update(self, delta_time, events):
        self.radius += self.speed * delta_time / 1000.0
        self.dirty = True

    def render(self, surface):
        self.aspect_ratio = surface.get_width() / surface.get_height()

        if not self.is_outside_world:
            self.real_radius = surface.get_width() * 0.5 * self.radius
            super(Pulse, self).render(surface)

    @property
    def is_outside_world(self):
        # check if all of the four
        # corners are inside the circle
        visible_height = 1.0 / self.aspect_ratio
        for x, y in ((-1, visible_height), (-1, -visible_height),
                     (1, -visible_height), (1, visible_height)):
            r2 = (x - self.x)**2 + (y - self.y)**2
            if r2 > self.radius**2:
                return False

        return True

    def draw(self):
        rect = self.surface.get_rect()
        width = 1 if self.real_radius > 1 else 0
        pygame.draw.ellipse(self.surface, (255, 255, 255),
                            pygame.Rect(rect.centerx - self.real_radius,
                                        rect.centery - self.real_radius,
                                        self.real_radius * 2,
                                        self.real_radius * 2),
                            width)

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
