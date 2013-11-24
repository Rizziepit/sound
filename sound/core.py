import math

from numpy.matrixlib import matrix
import pygame

from sound.utils import intersect_circles


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

    def construct_world_to_display_matrix(self, display_surface):
        if hasattr(self, '_display_width'):
            new_display_width = display_surface.get_width()
            new_display_height = display_surface.get_height()
            # if the dimensions haven't changed, the matrix
            # doesn't have to be recomputed
            if (new_display_width == self._display_width and
                new_display_height == self._display_height):
                return
            self._display_width = new_display_width
            self._display_height = new_display_height
            self._aspect_ratio = self._display_width / float(self._display_height)
        else:
            self._display_width = display_surface.get_width()
            self._display_height = display_surface.get_height()
            self._aspect_ratio = self._display_width / float(self._display_height)

        
        flip = matrix(((1, 0, 0), (0, -1, 0), (0, 0, 1)))
        translate = matrix(((1, 0, self._display_width * 0.5),
                            (0, 1, self._display_height * 0.5),
                            (0, 0, 1)))
        scale = matrix(((self._display_width * 0.5, 0, 0),
                        (0, self._display_width * 0.5, 1),
                        (0, 0, 1)))
        # order is flip, scale, translate
        mat = translate * (scale* flip)

        self.world_to_display_matrix = mat
        self.scale_matrix = scale
        self.dirty = True

    @property
    def display_rect(self):
        if not hasattr(self, '_display_rect'):
            vector_dims = matrix([[self.width], [self.height], [1]])
            vector_pos = matrix([[self.x], [self.y], [1]])
            vector_dims = self.scale_matrix * vector_dims
            vector_pos = self.world_to_display_matrix * vector_pos
            top_left = vector_pos - vector_dims * 0.5
            self._display_rect = pygame.Rect(top_left.item(0), top_left.item(1),
                                             vector_dims.item(0), vector_dims.item(1))
        return self._display_rect

    def pre_render(self, surface):
        self.construct_world_to_display_matrix(surface)
        if self.dirty and hasattr(self, '_display_rect'):
            delattr(self, '_display_rect')

    def render(self, surface):
        if not self.visible:
            return

        # check if this object is off-screen
        if not self.display_rect.colliderect(surface.get_rect()):
            return

        if self.dirty:
            self.surface = pygame.Surface((self.display_rect.width,
                                           self.display_rect.height),
                                          VisibleObject.DISPLAY_FLAGS)
            self.draw()
            self.dirty = False

        surface.blit(self.surface, self.display_rect)


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
        if not self.is_outside_display:
            super(Pulse, self).render(surface)

    @property
    def is_outside_display(self):
        # check if all of the four
        # corners are inside the circle
        visible_height = 1.0 / self._aspect_ratio
        for x, y in ((-1, visible_height), (-1, -visible_height),
                     (1, -visible_height), (1, visible_height)):
            r2 = (x - self.x)**2 + (y - self.y)**2
            if r2 > self.radius**2:
                return False

        return True

    def draw(self):
        rect = self.surface.get_rect()
        display_radius = self.radius * self.scale_matrix.item(0)
        width = 1 if display_radius > 1 else 0
        pygame.draw.ellipse(self.surface, (255, 255, 255),
                            pygame.Rect(rect.centerx - display_radius,
                                        rect.centery - display_radius,
                                        display_radius * 2,
                                        display_radius * 2),
                            width)

    def collide(self, obj):
        pass


class HiddenObject(CollidableObject, VisibleObject):

    def __init__(self, x, y, radius, colour):
        super(HiddenObject, self).__init__(x, y, radius * 2, radius * 2)
        self.colour = colour
        self.radius = radius
        self.pulses = set()

    def draw(self):
        pygame.draw.ellipse(self.surface, (32, 32, 32), self.surface.get_rect())
        display_to_object_surface_matrix = matrix([
            [1, 0, -self.display_rect.left],
            [0, 1, -self.display_rect.top],
            [0, 0, 1],
        ])

        for pulse in self.pulses:
            unit = self.display_rect.width / self.width
            radius = pulse.radius * unit
            arc_rect = self.surface.get_rect().copy()
            arc_rect.width = radius * 2
            arc_rect.height = radius * 2
            arc_rect.center = ((pulse.x - self.x) * unit + self.radius * unit,
                               (pulse.y - self.y) * -unit + self.radius * unit)
            width = 2 if radius > 2 else 0
            bands_half = 20
            for i in range(-bands_half, bands_half):
                arc_rect.width = radius * 2 + i
                arc_rect.height = radius * 2 + i
                divider = math.sqrt(bands_half + 1.0 + math.fabs(i) - bands_half)
                colour = [int(c / divider) for c in self.colour]
                result, points = intersect_circles(pulse.x, pulse.y,
                                                   self.x, self.y,
                                                   pulse.radius + i * 0.5 / unit,
                                                   self.radius)
                if not result or points is None:
                    continue

                for p in points:
                    point_on_display = self.world_to_display_matrix * p
                    point_on_surface = (display_to_object_surface_matrix
                                        * point_on_display)
                    pygame.draw.circle(self.surface, (255, 0, 0),
                                       (int(round(point_on_surface.item(0))),
                                        int(round(point_on_surface.item(1)))),
                                       1)

        self.pulses.clear()

    def collide(self, obj):
        # hidden objects collide with pulses in a special way
        if isinstance(obj, Pulse):
            # check for the non-colliding cases
            distance_sq = (obj.x - self.x)**2 + (obj.y - self.y)**2
            if distance_sq > (obj.radius + self.radius)**2:
                return
            self.pulses.add(obj)
            self.dirty = True
