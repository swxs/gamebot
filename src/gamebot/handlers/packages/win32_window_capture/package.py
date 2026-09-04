"""Win32 窗口客户区截图（ScreenCapture，需 bind hwnd）。"""

import cv2
import numpy as np
import win32con
import win32gui
import win32ui

from gamebot.protocols.types import Point
from gamebot.handlers.packages._hwnd import get_hwnd_with_name


class Win32WindowCapturePackage:
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

        if core.NAME:
            hwnd = get_hwnd_with_name(core.NAME)
            if hwnd == -1:
                raise RuntimeError(f"window not found: {core.NAME!r}")
        else:
            hwnd = win32gui.GetForegroundWindow()
            if not hwnd:
                raise RuntimeError("no foreground window to bind; set NAME or focus target window")
        return self.bind(hwnd)

    def _require_hwnd(self):
        if self._hwnd is None or self._hwnd == -1:
            raise RuntimeError("capture package not bound; call bind() or bind_from_env() first")
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

    def client_to_screen(self, point: Point) -> Point:
        hwnd = self._require_hwnd()
        sx, sy = win32gui.ClientToScreen(hwnd, (point.x, point.y))
        return Point(sx, sy)
