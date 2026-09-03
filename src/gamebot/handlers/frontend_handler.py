import win32api
import win32gui
import win32con
import win32ui
from .base_handler import Base


class FrontEnd(Base):
    name = "frontend"

    @classmethod
    def get_point(cls, hwnd):
        return win32gui.GetCursorPos()

    @classmethod
    def move_to(cls, x, y):
        win32api.mouse_event(
            win32con.MOUSEEVENTF_ABSOLUTE | win32con.MOUSEEVENTF_MOVE,
            x * 65535 // 3840,
            y * 65535 // 2160,
        )
        return True

    @classmethod
    def left_click_at_point(cls, hwnd, point):
        win32api.mouse_event(
            win32con.MOUSEEVENTF_ABSOLUTE | win32con.MOUSEEVENTF_LEFTDOWN | win32con.MOUSEEVENTF_LEFTUP,
            point[0] * 65535 // 2560,
            point[1] * 65535 // 1440,
        )
        return True

    @classmethod
    def right_click_at_point(cls, hwnd, point):
        win32api.mouse_event(
            win32con.MOUSEEVENTF_RIGHTDOWN | win32con.MOUSEEVENTF_RIGHTUP,
            point[0] * 65535 // 2560,
            point[1] * 65535 // 1440,
        )
        return True
