import sys
import pygame

from sound.render import Canvas
from sound.resources import load_image
from sound import event as s_event
from sound import core


DEBUG = True
pygame.init()
canvas = Canvas(900, 300, background=(0, 0, 0))
clock = pygame.time.Clock()
keys_down = set()
mouse_down = set()
objects = [
    core.HiddenObject(0.5, 0.1, 0.05, (0, 255, 255)),
    core.Pulse(-0.5, -0.1, 0.1),
    core.Pulse(0, 0, 0.2),
    core.Pulse(0, 0, 0.1),
    core.Pulse(0.3, 0.2, 0.15),
]
visible_objects = filter(lambda x: isinstance(x, core.VisibleObject), objects)
updateable_objects = filter(lambda x: isinstance(x, core.UpdateableObject), objects)
collidable_objects = filter(lambda x: isinstance(x, core.CollidableObject), objects)

# show invisible objects in the world
if DEBUG:
    for obj in visible_objects:
        obj.visible = True


def handle_events():
    '''
    Processes events on the event queue. Window-level
    events are handled here (e.g. resize and exit). The
    rest of the events are added to a game events dict
    which game objects can use. Compound events, like
    mouse drags, mouse clicks and key presses are added
    to the game events dict.
    '''
    game_events = {}

    for event in pygame.event.get():
        # handle window events
        if event.type == pygame.QUIT:
            sys.exit()
        elif event.type == pygame.VIDEORESIZE:
            canvas.handle_resize(event.w, event.h)
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

        for obj in updateable_objects:
            if isinstance(obj, core.UpdateableObject):
                obj.update(delta_time, game_events)

        for i in range(len(collidable_objects)):
            obj1 = collidable_objects[i]
            for j in range(i + 1, len(collidable_objects)):
                obj2 = collidable_objects[j]
                obj1.collide(obj2)
                obj2.collide(obj1)

        canvas.render(
            visible_objects,
            (('FPS', fps),
             ('Frame time', '%s ms' % delta_time))
        )
