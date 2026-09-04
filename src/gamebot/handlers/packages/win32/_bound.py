"""Win32 handler 共享：hwnd 绑定。"""

import win32gui

from gamebot.handlers.packages._hwnd import get_hwnd_with_name


class Win32BoundMixin:
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
            raise RuntimeError("handler not bound; call bind() or bind_from_env() first")
        return self._hwnd
