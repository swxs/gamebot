import cv2
import functools


import numpy as np


@functools.lru_cache
def get_template_info(file):
    template = cv2.imread(file, cv2.IMREAD_GRAYSCALE)
    w, h = template.shape[::-1]
    return template, w, h


def diff_image(total, target, sens=0.8):
    result = cv2.matchTemplate(
        cv2.cvtColor(total, cv2.COLOR_BGR2GRAY),
        target,
        cv2.TM_CCOEFF_NORMED,
    )
    return np.where(result >= sens)
