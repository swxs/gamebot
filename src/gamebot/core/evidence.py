"""一次运行的客户区截图、控件树和最近步骤。"""

import json
import os

import numpy as np


def png_bytes(image) -> bytes:
    if image is None:
        return b""
    if isinstance(image, (bytes, bytearray)):
        return bytes(image)
    import cv2

    if not isinstance(image, np.ndarray) or image.size == 0:
        return b""
    ok, encoded = cv2.imencode(".png", image)
    if not ok:
        return b""
    return encoded.tobytes()


def capture_image(group):
    try:
        browser = group.pkg("browser")
    except KeyError:
        browser = None
    if browser is not None and getattr(browser, "has_page", lambda: False)():
        try:
            return browser.screenshot()
        except Exception:
            return None
    for name in ("capture", "desktop"):
        try:
            pkg = group.pkg(name)
        except KeyError:
            continue
        if not hasattr(pkg, "capture"):
            continue
        try:
            return pkg.capture()
        except Exception:
            return None
    return None


def capture_tree(group) -> str:
    try:
        controls = group.pkg("controls")
    except KeyError:
        return ""
    try:
        return controls.read_tree() or ""
    except Exception:
        return ""


class EvidenceWriter:
    def __init__(self, directory: str):
        self.directory = directory
        self._previous = None
        self._steps: list[str] = []

    def write(self, group, step: str):
        current = png_bytes(capture_image(group))
        previous = b"" if self._previous is None else self._previous
        tree = capture_tree(group)
        self._steps.append(str(step))
        recent = self._steps[-5:]
        os.makedirs(self.directory, exist_ok=True)
        with open(os.path.join(self.directory, "previous.png"), "wb") as handle:
            handle.write(previous)
        with open(os.path.join(self.directory, "current.png"), "wb") as handle:
            handle.write(current)
        with open(os.path.join(self.directory, "tree.txt"), "w", encoding="utf-8") as handle:
            handle.write(tree)
        with open(os.path.join(self.directory, "steps.json"), "w", encoding="utf-8") as handle:
            json.dump(recent, handle, ensure_ascii=False)
        self._previous = current
        return recent
