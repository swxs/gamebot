"""Win32 BitBlt 客户区截图（ScreenCapture）。"""

import cv2
import numpy as np
import win32con
import win32gui
import win32ui

from gamebot.protocols.types import Point
from gamebot.handlers.packages.win32._bound import Win32BoundMixin


class Win32CaptureHandler(Win32BoundMixin):

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
