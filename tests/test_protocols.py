from gamebot.protocols import (
    ClipboardAccess,
    KeyboardInput,
    PointerInput,
    ScreenCapture,
    TemplateMatcher,
    WindowControl,
)
from gamebot.protocols.types import MatchResult, Point, Rect


class _FakeScreenCapture:
    def capture(self):
        return None


class _FakePointer:
    def move_to(self, point, duration=0.1):
        return True

    def click(self, point):
        return True

    def right_click(self, point):
        return True


class _FakeKeyboard:
    def press(self, key):
        return True

    def type_text(self, text):
        return True


class _FakeMatcher:
    def find(self, screen, template_path, sens=0.8):
        return None


class _FakeClipboard:
    def read(self):
        return ""

    def write(self, text):
        return True


class _FakeWindowControl:
    def focus(self):
        return True

    def restore(self):
        return True

    def minimize(self):
        return True


def test_protocols_runtime_checkable():
    assert isinstance(_FakeScreenCapture(), ScreenCapture)
    assert isinstance(_FakePointer(), PointerInput)
    assert isinstance(_FakeKeyboard(), KeyboardInput)
    assert isinstance(_FakeMatcher(), TemplateMatcher)
    assert isinstance(_FakeClipboard(), ClipboardAccess)
    assert isinstance(_FakeWindowControl(), WindowControl)


def test_types_point_rect():
    p = Point(1, 2)
    r = Rect(0, 0, 10, 20)
    assert p.x == 1
    assert r.center == Point(5, 10)
    m = MatchResult(top_left=Point(0, 0), bottom_right=Point(10, 10))
    assert m.center == Point(5, 5)
