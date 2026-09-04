import cv2
import numpy as np
import win32api
import win32con
import win32gui
import win32ui

from gamebot.protocols.types import Point
from gamebot.handlers.packages._hwnd import get_hwnd_with_name


class Win32BackendPackage:
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
        hwnd_dc = win32gui.GetWindowDC(hwnd)
        mfc_dc = win32ui.CreateDCFromHandle(hwnd_dc)
        mfc_handler = mfc_dc.GetHandleAttrib()
        win32gui.SendMessage(
            hwnd,
            win32con.WM_PRINT,
            mfc_handler,
            win32con.PRF_CLIENT | win32con.PRF_OWNED | win32con.PRF_ERASEBKGND | win32con.PRF_NONCLIENT,
        )
        save_dc = mfc_dc.CreateCompatibleDC()
        client = win32gui.GetClientRect(hwnd)
        w = client[2] * 3 // 2
        h = client[3] * 3 // 2
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

    def move_to(self, point: Point, duration: float = 0.1):
        hwnd = self._require_hwnd()
        start = win32gui.GetCursorPos()
        end = (point.x, point.y)
        tmp_x = end[0] - start[0]
        tmp_y = end[1] - start[1]
        steps = max(abs(tmp_x), abs(tmp_y)) // 10 or 1
        start_tmp = win32api.MAKELONG(start[0], start[1])
        win32gui.SendMessage(hwnd, win32con.WM_MOUSEMOVE, 0, start_tmp)
        for i in range(steps):
            current = (
                int(start[0] + tmp_x / steps * (i + 1)),
                int(start[1] + tmp_y / steps * (i + 1)),
            )
            win32gui.SendMessage(hwnd, win32con.WM_MOUSEMOVE, 0, win32api.MAKELONG(current[0], current[1]))
        end_tmp = win32api.MAKELONG(end[0], end[1])
        win32gui.SendMessage(hwnd, win32con.WM_MOUSEMOVE, 0, end_tmp)
        return True

    def click(self, point: Point):
        hwnd = self._require_hwnd()
        tmp = win32api.MAKELONG(point.x, point.y)
        win32gui.SendMessage(hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, tmp)
        win32gui.SendMessage(hwnd, win32con.WM_LBUTTONUP, 0, tmp)
        return True

    def right_click(self, point: Point):
        hwnd = self._require_hwnd()
        tmp = win32api.MAKELONG(point.x, point.y)
        win32gui.SendMessage(hwnd, win32con.WM_RBUTTONDOWN, win32con.MK_RBUTTON, tmp)
        win32gui.SendMessage(hwnd, win32con.WM_RBUTTONUP, 0, tmp)
        return True

    def press(self, key: str):
        hwnd = self._require_hwnd()
        vk = ord(key.upper()) if len(key) == 1 else 0
        win32gui.SendMessage(hwnd, win32con.WM_KEYDOWN, vk, 0)
        win32gui.SendMessage(hwnd, win32con.WM_KEYUP, vk, 0)
        return True

    def type_text(self, text: str):
        hwnd = self._require_hwnd()
        for ch in text:
            win32gui.SendMessage(hwnd, win32con.WM_CHAR, ord(ch), 0)
        return True

    def focus(self):
        hwnd = self._require_hwnd()
        win32gui.SetForegroundWindow(hwnd)
        return True

    def restore(self):
        hwnd = self._require_hwnd()
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        return True

    def minimize(self):
        hwnd = self._require_hwnd()
        win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)
        return True
