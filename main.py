import sys
import pygame

from sound.render import Canvas
from sound.resources import load_image
from sound import event as s_event


pygame.init()
canvas = Canvas(800, 600)
clock = pygame.time.Clock()
keys_down = set()
mouse_down = set()
objects = [
]


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

        for obj in objects:
            obj.update(delta_time, game_events)

        canvas.render(
            objects,
            (('FPS', fps),
             ('Frame time', '%s ms' % delta_time))
        )
