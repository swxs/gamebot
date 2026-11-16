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


def test_capture_bind_title(monkeypatch):
    monkeypatch.setattr(
        "gamebot.handlers.packages.win32._bound.get_hwnd_with_name",
        lambda name: 12345 if name == "TestWindow" else -1,
    )
    pkg = Win32Package.install_capture().bind_title("TestWindow")
    assert pkg._hwnd == 12345


def test_capture_bind_title_rejects_empty():
    pkg = Win32Package.install_capture()
    with pytest.raises(RuntimeError, match="non-empty"):
        pkg.bind_title("")


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


def test_find_all_and_region(tmp_path):
    import cv2

    from gamebot.protocols.types import Rect

    pattern = np.zeros((12, 12, 3), dtype=np.uint8)
    pattern[0:6, 0:6] = (255, 0, 0)
    pattern[6:12, 6:12] = (0, 255, 0)
    pattern[0:6, 6:12] = (0, 0, 255)
    screen = np.zeros((100, 100, 3), dtype=np.uint8)
    screen[10:22, 10:22] = pattern
    screen[70:82, 70:82] = pattern
    template_path = tmp_path / "mark.png"
    cv2.imwrite(str(template_path), pattern)
    matcher = OpenCVPackage.install_matcher()
    hits = matcher.find_all(screen, str(template_path), sens=0.99)
    assert len(hits) == 2
    missed = matcher.find(screen, str(template_path), sens=0.99, region=Rect(0, 0, 8, 8))
    assert missed is None
    found = matcher.find(screen, str(template_path), sens=0.99, region=Rect(8, 8, 20, 20))
    assert found is not None
    assert found.top_left.x >= 8


def test_wait_timeout_returns_none():
    matcher = OpenCVPackage.install_matcher()
    matcher.find = lambda *args, **kwargs: None

    class _Blank:
        def capture(self):
            return np.zeros((20, 20, 3), dtype=np.uint8)

    assert matcher.wait(_Blank(), "unused.png", timeout=0, interval=5) is None


def test_ocr_empty_result():
    from gamebot.protocols.types import OcrHit, Rect

    image = np.zeros((4, 4, 3), dtype=np.uint8)
    handler = Win32Package.install_ocr()
    handler._recognize = lambda _image: [OcrHit("跑通", Rect(1, 2, 3, 4))]
    assert handler.find_text(image, "没有") is None
    assert handler.find_text(image, "跑").text == "跑通"
    handler._recognize = lambda _image: []
    assert handler.read(image) == []


def test_controls_reads_injected_dump():
    handler = Win32Package.install_controls()
    handler._hwnd = 7
    handler._dump = lambda hwnd: f"按钮 {hwnd}"
    assert handler.read_tree() == "按钮 7"
