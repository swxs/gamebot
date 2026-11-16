"""Win32 handler 共享：hwnd 绑定。"""

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

    def bind_title(self, title: str):
        if not isinstance(title, str) or title.strip() == "":
            raise RuntimeError("window title must be a non-empty string")
        hwnd = get_hwnd_with_name(title)
        if hwnd == -1:
            raise RuntimeError(f"window not found: {title!r}")
        return self.bind(hwnd)

    def _require_hwnd(self):
        if self._hwnd is None or self._hwnd == -1:
            raise RuntimeError("handler not bound; call bind() or bind_title() first")
        return self._hwnd
