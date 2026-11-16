import random
import time
from typing import Optional

import numpy as np

from gamebot.protocols.types import MatchResult, Point, Rect
from gamebot.handlers.packages.opencv._cv import diff_image, get_template_info, locate_peaks


def _crop(screen: np.ndarray, region: Optional[Rect]):
    if region is None:
        return screen, 0, 0
    view = screen[region.y : region.y + region.height, region.x : region.x + region.width]
    return view, region.x, region.y


def _shift(match: MatchResult, origin_x: int, origin_y: int) -> MatchResult:
    if origin_x == 0 and origin_y == 0:
        return match
    return MatchResult(
        top_left=Point(match.top_left.x + origin_x, match.top_left.y + origin_y),
        bottom_right=Point(match.bottom_right.x + origin_x, match.bottom_right.y + origin_y),
    )


class OpenCVMatcherHandler:

    def find(
        self,
        screen: np.ndarray,
        template_path: str,
        sens: float = 0.8,
        region: Optional[Rect] = None,
    ) -> Optional[MatchResult]:
        view, origin_x, origin_y = _crop(screen, region)
        if view.size == 0:
            return None
        target, width, height = get_template_info(template_path)
        loc = diff_image(view, target, sens=sens)
        if len(loc[0]) == 0:
            return None
        pt = random.choice(list(zip(*loc[::-1])))
        match = MatchResult(
            top_left=Point(pt[0], pt[1]),
            bottom_right=Point(pt[0] + width, pt[1] + height),
        )
        return _shift(match, origin_x, origin_y)

    def find_all(
        self,
        screen: np.ndarray,
        template_path: str,
        sens: float = 0.8,
        region: Optional[Rect] = None,
    ) -> list[MatchResult]:
        view, origin_x, origin_y = _crop(screen, region)
        if view.size == 0:
            return []
        target, width, height = get_template_info(template_path)
        peaks = locate_peaks(view, target, sens=sens)
        matches = []
        for x, y in peaks:
            matches.append(
                _shift(
                    MatchResult(
                        top_left=Point(x, y),
                        bottom_right=Point(x + width, y + height),
                    ),
                    origin_x,
                    origin_y,
                )
            )
        return matches

    def wait(
        self,
        capture,
        template_path: str,
        sens: float = 0.8,
        timeout: float = 10,
        interval: float = 0.5,
        region: Optional[Rect] = None,
    ) -> Optional[MatchResult]:
        deadline = time.monotonic() + timeout
        while True:
            hit = self.find(capture.capture(), template_path, sens=sens, region=region)
            if hit is not None:
                return hit
            if time.monotonic() >= deadline:
                return None
            time.sleep(interval)

    def find_and_click(
        self,
        capture_pkg,
        pointer_pkg,
        template_path,
        sens=0.8,
    ) -> bool:
        screen = capture_pkg.capture()
        match = self.find(screen, template_path, sens=sens)
        if match is None:
            return False
        point = match.center
        if capture_pkg is not pointer_pkg and hasattr(capture_pkg, "client_to_screen"):
            point = capture_pkg.client_to_screen(point)
        return pointer_pkg.click(point)
