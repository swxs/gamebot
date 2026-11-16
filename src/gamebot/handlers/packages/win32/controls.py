"""已绑定窗口的 UI Automation 控件树。不注入游戏进程。"""

from gamebot.handlers.packages.win32._bound import Win32BoundMixin


def dump_window(hwnd: int) -> str:
    from pywinauto import Application

    root = Application(backend="uia").connect(handle=hwnd).window(handle=hwnd)
    lines = []

    def walk(ctrl, depth: int):
        try:
            text = ctrl.window_text()
        except Exception:
            text = ""
        try:
            control_type = ctrl.element_info.control_type
        except Exception:
            control_type = ""
        lines.append(f"{'  ' * depth}{control_type} {text}".rstrip())
        try:
            children = ctrl.children()
        except Exception:
            children = []
        for child in children:
            walk(child, depth + 1)

    walk(root, 0)
    return "\n".join(lines)


class Win32ControlsHandler(Win32BoundMixin):
    def __init__(self, hwnd: int | None = None, dump=None):
        super().__init__(hwnd)
        self._dump = dump or dump_window

    def read_tree(self) -> str:
        return self._dump(self._require_hwnd())
