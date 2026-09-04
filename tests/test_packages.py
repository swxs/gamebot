import numpy as np
import pytest

from gamebot.handlers.packages.opencv import OpenCVPackage
from gamebot.handlers.packages.pyauto import PyAutoPackage
from gamebot.handlers.packages.win32 import Win32Package
from gamebot.protocols.types import Point


class _FakeCapture:
    def __init__(self):
        self._screen = np.zeros((80, 80, 3), dtype=np.uint8)
        self._screen[20:40, 20:40] = (0, 255, 0)

    def capture(self):
        return self._screen

    def client_to_screen(self, point: Point) -> Point:
        return Point(point.x + 100, point.y + 200)


class _FakePointer:
    def __init__(self):
        self.clicked = None

    def click(self, point):
        self.clicked = point
        return True


def test_pyauto_no_bind(monkeypatch):
    monkeypatch.setattr("pyautogui.moveTo", lambda *a, **k: None)
    pkg = PyAutoPackage.install_pointer_direct()
    assert pkg.move_to(Point(0, 0)) is True


def test_capture_unbound_raises():
    pkg = Win32Package.install_capture()
    with pytest.raises(RuntimeError, match="not bound"):
        pkg.capture()


def test_capture_bind_from_env(monkeypatch):
    monkeypatch.setattr("gamebot.core.NAME", "TestWindow")
    monkeypatch.setattr(
        "gamebot.handlers.packages.win32._bound.get_hwnd_with_name",
        lambda name: 12345,
    )
    pkg = Win32Package.install_capture().bind_from_env()
    assert pkg._hwnd == 12345


def test_opencv_find(tmp_path):
    screen = np.zeros((100, 100, 3), dtype=np.uint8)
    screen[30:50, 30:50] = (255, 0, 0)
    template_path = tmp_path / "tpl.png"
    import cv2

    cv2.imwrite(str(template_path), screen[30:50, 30:50])
    matcher = OpenCVPackage.install_matcher()
    hit = matcher.find(screen, str(template_path), sens=0.8)
    assert hit is not None
    w = hit.bottom_right.x - hit.top_left.x
    h = hit.bottom_right.y - hit.top_left.y
    assert w == 20
    assert h == 20


def test_find_and_click_orchestration():
    capture = _FakeCapture()
    pointer = _FakePointer()
    matcher = OpenCVPackage.install_matcher()

    def fake_find(screen, path, sens=0.8):
        from gamebot.protocols.types import MatchResult

        return MatchResult(top_left=Point(20, 20), bottom_right=Point(40, 40))

    matcher.find = fake_find
    assert matcher.find_and_click(capture, pointer, "__memory__") is True
    assert pointer.clicked == Point(130, 230)


def test_find_and_click_same_pkg_skips_screen_offset():
    class _Combined(_FakeCapture, _FakePointer):
        pass

    combined = _Combined()
    matcher = OpenCVPackage.install_matcher()

    def fake_find(screen, path, sens=0.8):
        from gamebot.protocols.types import MatchResult

        return MatchResult(top_left=Point(20, 20), bottom_right=Point(40, 40))

    matcher.find = fake_find
    assert matcher.find_and_click(combined, combined, "__memory__") is True
    assert combined.clicked == Point(30, 30)


def test_pyperclip_read_write(monkeypatch):
    store = {"v": ""}

    monkeypatch.setattr("pyperclip.paste", lambda: store["v"])
    monkeypatch.setattr("pyperclip.copy", lambda v: store.update({"v": v}))

    from gamebot.handlers.packages.pyperclip import PyperclipPackage

    pkg = PyperclipPackage.install_clipboard()
    pkg.write("hello")
    assert pkg.read() == "hello"


def test_check_packages_dedupes_stack():
    from gamebot.handlers.packages._package import check_packages

    seen = []

    class _Pkg:
        @classmethod
        def check_deps(cls):
            seen.append(1)

    class _Handler:
        __package__ = _Pkg

    check_packages({"a": _Handler(), "b": _Handler()})
    assert len(seen) == 1
