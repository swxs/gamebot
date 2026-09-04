"""Package 内部共享：窗口句柄查找（不对外 export）。"""

import win32gui


def get_hwnd_list():
    hwnd_list = []

    def is_visible_tree(hwnd):
        return win32gui.IsWindow(hwnd) and win32gui.IsWindowEnabled(hwnd) and win32gui.IsWindowVisible(hwnd)

    def _get_hwnd(hwnd, mouse):
        if is_visible_tree(hwnd):
            hwnd_list.append(
                {
                    "hwnd": hwnd,
                    "title": win32gui.GetWindowText(hwnd),
                }
            )

    win32gui.EnumWindows(_get_hwnd, 0)
    return hwnd_list


def get_hwnd_with_name(name):
    for item in get_hwnd_list():
        if item.get("title") == name:
            return item["hwnd"]
    return -1
