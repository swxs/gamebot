import functools
import random

import cv2
import numpy as np


@functools.lru_cache
def get_template_info(file):
    template = cv2.imread(file, cv2.IMREAD_GRAYSCALE)
    w, h = template.shape[::-1]
    return template, w, h


def diff_image(total, target, sens=0.8):
    gray = cv2.cvtColor(total, cv2.COLOR_BGR2GRAY) if total.ndim == 3 else total
    if gray.shape[0] < target.shape[0] or gray.shape[1] < target.shape[1]:
        return (np.array([]), np.array([]))
    result = cv2.matchTemplate(gray, target, cv2.TM_CCOEFF_NORMED)
    return np.where(result >= sens)


def locate_peaks(total, target, sens=0.8):
    """按分数从高到低取互不重叠的命中，没有则空列表。"""
    if total.size == 0 or target.size == 0:
        return []
    gray = cv2.cvtColor(total, cv2.COLOR_BGR2GRAY) if total.ndim == 3 else total
    if gray.shape[0] < target.shape[0] or gray.shape[1] < target.shape[1]:
        return []
    result = cv2.matchTemplate(gray, target, cv2.TM_CCOEFF_NORMED)
    ys, xs = np.where(result >= sens)
    if len(xs) == 0:
        return []
    height, width = target.shape[:2]
    order = np.argsort(-result[ys, xs])
    picked = []
    min_dx = max(width // 2, 1)
    min_dy = max(height // 2, 1)
    for index in order:
        x, y = int(xs[index]), int(ys[index])
        if any(abs(x - px) < min_dx and abs(y - py) < min_dy for px, py in picked):
            continue
        picked.append((x, y))
    return picked
