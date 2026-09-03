import os

from gamebot import core


def get_file_path(self, filename):
    return os.path.join(core.FIEL_PATH, filename)
