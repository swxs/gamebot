import cv2
import numpy as np
import pyautogui
import win32con
import win32gui
import win32ui

from gamebot.protocols.types import Point
from gamebot.handlers.packages._hwnd import get_hwnd_with_name


class PyAutoDesktopPackage:
    def __init__(self, hwnd: int | None = None):
        self._hwnd = hwnd

    @classmethod
    def unbound(cls):
        return cls()

    def bind(self, hwnd: int):
        self._hwnd = hwnd
        return self

    def bind_from_env(self):
        from gamebot import core

        if core.NAME is None:
            raise RuntimeError("NAME not set in environment")
        hwnd = get_hwnd_with_name(core.NAME)
        if hwnd == -1:
            raise RuntimeError(f"window not found: {core.NAME!r}")
        return self.bind(hwnd)

    def _require_hwnd(self):
        if self._hwnd is None or self._hwnd == -1:
            raise RuntimeError("desktop package not bound; call bind() or bind_from_env() first")
        return self._hwnd

    def capture(self):
        hwnd = self._require_hwnd()
        left, top, right, bottom = win32gui.GetClientRect(hwnd)
        w, h = right - left, bottom - top
        hwnd_dc = win32gui.GetWindowDC(hwnd)
        mfc_dc = win32ui.CreateDCFromHandle(hwnd_dc)
        save_dc = mfc_dc.CreateCompatibleDC()
        save_bitmap = win32ui.CreateBitmap()
        save_bitmap.CreateCompatibleBitmap(mfc_dc, w, h)
        save_dc.SelectObject(save_bitmap)
        save_dc.BitBlt((0, 0), (w, h), mfc_dc, (0, 0), win32con.SRCCOPY)
        signed = save_bitmap.GetBitmapBits(True)
        img = np.frombuffer(signed, dtype=np.uint8)
        img.shape = (h, w, 4)
        win32gui.DeleteObject(save_bitmap.GetHandle())
        save_dc.DeleteDC()
        mfc_dc.DeleteDC()
        win32gui.ReleaseDC(hwnd, hwnd_dc)
        return cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

    def move_to(self, point: Point, duration: float = 0.5):
        pyautogui.moveTo(point.x, point.y, duration=duration, tween=pyautogui.easeInOutQuad)
        return True

    def click(self, point: Point):
        pyautogui.click(point.x, point.y)
        return True

    def right_click(self, point: Point):
        pyautogui.rightClick(point.x, point.y)
        return True

    def press(self, key: str):
        pyautogui.press(key)
        return True

    def type_text(self, text: str):
        pyautogui.typewrite(text, interval=0.05)
        return True
