import os
import glob

import pygame


ASSETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          '../assets/')
IMAGE_DIR = os.path.join(ASSETS_DIR, 'images')
SOUND_DIR = os.path.join(ASSETS_DIR, 'sounds')


class InvalidResource(Exception):
    pass


def load_image(filename):
    filepath = get_resource_filepath(IMAGE_DIR, filename)
    try:
        return pygame.image.load(filepath)
    except pygame.error:
        raise InvalidResource("'%s' is not a valid image resource (full path: %s)"
                              % (filename, filepath))


def load_sound(filename):
    filepath = get_resource_filepath(SOUND_DIR, filename)
    try:
        return pygame.mixer.Sound(filepath)
    except pygame.error:
        raise InvalidResource("'%s' is not a valid sound resource (full path: %s)"
                              % (filename, filepath))


def get_resource_filepath(base_dir, filename):
    index = filename.rfind('.')
    if index != -1:
        return os.path.join(IMAGE_DIR, filename)
    else:
        filepaths = glob.glob('%s.*' % os.path.join(IMAGE_DIR, filename))
        if not filepaths:
            raise InvalidResource("No resource matching '%s.*'"
                                  % os.path.join(IMAGE_DIR, filename))
        elif len(filepaths) > 1:
            raise InvalidResource("'%s' is ambiguous, it matches %s" % filepaths)
        return filepaths[0]
