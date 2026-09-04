import random
from typing import Optional

import numpy as np

from gamebot.protocols.types import MatchResult, Point
from gamebot.handlers.packages.opencv_matcher._cv import diff_image, get_template_info


class OpenCVMatcherPackage:
    def find(
        self,
        screen: np.ndarray,
        template_path: str,
        sens: float = 0.8,
    ) -> Optional[MatchResult]:
        target, w, h = get_template_info(template_path)
        loc = diff_image(screen, target, sens=sens)
        if len(loc[0]) == 0:
            return None
        pt = random.choice(list(zip(*loc[::-1])))
        top_left = Point(pt[0], pt[1])
        bottom_right = Point(pt[0] + w, pt[1] + h)
        return MatchResult(top_left=top_left, bottom_right=bottom_right)

    def find_and_click(self, desktop_pkg, template_path: str, sens: float = 0.8) -> bool:
        screen = desktop_pkg.capture()
        match = self.find(screen, template_path, sens=sens)
        if match is None:
            return False
        return desktop_pkg.click(match.center)
