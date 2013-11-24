import sys
import random
import math

import pygame

from sound.render import Canvas
from sound import event as s_event
from sound import core


DEBUG = True
pygame.init()
canvas = Canvas(900, 900, background=(0, 0, 0))
clock = pygame.time.Clock()
keys_down = set()
mouse_down = set()
player = core.Player(0, 0, 1.5)
objects = set([player])
visible_objects = set(filter(lambda x: isinstance(x, core.VisibleObject), objects))
updateable_objects = set(filter(lambda x: isinstance(x, core.UpdateableObject), objects))
collidable_objects = set(filter(lambda x: isinstance(x, core.CollidableObject), objects))

# generate some random hidden objects
for i in range(10):
    angle = random.random() * 2.0 * math.pi
    print angle
    distance = random.random()
    x = distance * math.cos(angle)
    y = distance * math.sin(angle)
    radius = random.random() * 0.2 + 0.05
    colour = (random.randint(0, 255),
              random.randint(0, 255),
              random.randint(0, 255))
    obj = core.HiddenObject(x, y, radius, colour)
    objects.add(obj)
    visible_objects.add(obj)
    collidable_objects.add(obj)

# show invisible objects in the world
for obj in objects:
    obj.debug = DEBUG


def handle_events():
    '''
    Processes events on the event queue. Window-level
    events are handled here (e.g. resize and exit). The
    rest of the events are added to a game events dict
    which game objects can use. Compound events, like
    mouse drags, mouse clicks and key presses are added
    to the game events dict.
    '''
    game_events = {'keys_down': keys_down,
                   'mouse_down': mouse_down}

    for event in pygame.event.get():
        # handle window events
        if event.type == pygame.QUIT:
            sys.exit()
        elif event.type == pygame.VIDEORESIZE:
            canvas.handle_resize(event.w, event.h)
        # special game-logic event - might move out later
        elif event.type == s_event.ADDPULSE:
            event.pulse.debug = DEBUG
            for li in (objects, visible_objects, updateable_objects,
                       collidable_objects):
                li.add(event.pulse)
        # handle game events
        else:
            game_events.setdefault(event.type, [])
            game_events[event.type].append(event)
            # track KEYPRESS events
            # KEYPRESS: KEYDOWN + KEYUP
            if event.type == pygame.KEYDOWN:
                keys_down.add(event.key)
            elif event.type == pygame.KEYUP:
                if event.key in keys_down:
                    keys_down.remove(event.key)
                    # handle window escape event
                    if event.key == 27:
                        sys.exit()
                    game_events.setdefault(s_event.KEYPRESS, [])
                    game_events[s_event.KEYPRESS].append(
                        pygame.event.Event(s_event.KEYPRESS,
                                           key=event.key,
                                           mod=event.mod)
                    )
            # track MOUSEBUTTONDRAG and MOUSEBUTTONCLICK events
            # MOUSEBUTTONDRAG: MOUSEBUTTONDOWN + MOUSEMOTION
            # MOUSEBUTTONCLICK: MOUSEBUTTONDOWN + MOUSEBUTTONUP
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_down.add(event.button)
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button in mouse_down:
                    mouse_down.remove(event.button)
                    game_events.setdefault(s_event.MOUSEBUTTONCLICK, [])
                    game_events[s_event.MOUSEBUTTONCLICK].append(
                        pygame.event.Event(s_event.MOUSEBUTTONCLICK,
                                           button=event.button,
                                           pos=event.pos)
                    )
            elif event.type == pygame.MOUSEMOTION:
                for button in mouse_down:
                    game_events.setdefault(s_event.MOUSEBUTTONDRAG, [])
                    game_events[s_event.MOUSEBUTTONDRAG].append(
                        pygame.event.Event(s_event.MOUSEBUTTONDRAG,
                                           button=button,
                                           pos=event.pos,
                                           rel=event.rel)
                    )

    return game_events


if __name__ == '__main__':
    while True:
        delta_time = clock.tick(60)
        fps = clock.get_fps()

        # handle events
        game_events = handle_events()

        dead_objects = []

        for obj in updateable_objects:
            if isinstance(obj, core.UpdateableObject):
                obj.update(delta_time, game_events)
                if obj.dead:
                    dead_objects.append(obj)

        collidable_list = list(collidable_objects)
        for i in range(len(collidable_list)):
            obj1 = collidable_list[i]
            for j in range(i + 1, len(collidable_list)):
                obj2 = collidable_list[j]
                obj1.collide(obj2)
                obj2.collide(obj1)

        canvas.render(
            visible_objects,
            (('FPS', fps),
             ('Frame time', '%s ms' % delta_time))
        )

        # remove dead objects
        for obj in dead_objects:
            if isinstance(obj, core.UpdateableObject):
                updateable_objects.remove(obj)
            if isinstance(obj, core.CollidableObject):
                collidable_objects.remove(obj)
            if isinstance(obj, core.VisibleObject):
                visible_objects.remove(obj)
            objects.remove(obj)

