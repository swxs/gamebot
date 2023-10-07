import os
import cv2
import time

import win32api
import win32gui
import win32con
import win32ui
import random
import numpy as np
import functools

import core
from .utils.point_utils import Point
from .utils import hwnd_utils, cv_utils, point_utils


class Base:
    name = "base"

    def __init__(self) -> None:
        pass

    def start(self, **kwargs):
        pass

    def screen(self, filename):
        pass

    def find_assents(self, total, target_path, sens=0.8):
        target, w, h = cv_utils.get_template_info(target_path)
        loc = cv_utils.diff_image(total, target, sens=sens)
        if len(loc[0]) != 0:
            pt = random.choice(list(zip(*loc[::-1])))
            return (
                point_utils.Point(pt[0], pt[1]),
                point_utils.Point(pt[0] + w, pt[1] + h),
            )
        else:
            return (
                None,
                None,
            )

    def move_to(self, point: Point, duration=0.1):
        pass

    def left_click_at_point(self, point: Point):
        pass

    def right_click_at_point(self, point: Point):
        pass
