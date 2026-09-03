import win32api
import win32gui
import win32con
import win32ui


def get_children_hwnd(parent_hwnd):
    """
    获得parent的所有子窗口句柄
    返回子窗口句柄列表
    """
    if not parent_hwnd:
        return
    hwndChildList = []
    try:
        win32gui.EnumChildWindows(
            parent_hwnd,
            lambda hwnd, param: param.append((hwnd, win32gui.GetWindowText(hwnd))),
            hwndChildList,
        )
    except Exception as e:
        pass
    return hwndChildList


def find_idxSubHandle(pHandle, winClass, index=0):
    """
    已知子窗口的窗体类名
    寻找第index号个同类型的兄弟窗口
    """
    handle = win32gui.FindWindowEx(pHandle, 0, winClass, None)
    while index > 0:
        handle = win32gui.FindWindowEx(pHandle, handle, winClass, None)
        index -= 1
    return handle


def find_subHandle(pHandle, winClassList):
    """
    递归寻找子窗口的句柄
    pHandle是祖父窗口的句柄
    winClassList是各个子窗口的class列表，父辈的list-index小于子辈
    """
    if len(winClassList) == 1:
        return find_idxSubHandle(pHandle, winClassList[0][0], winClassList[0][1])
    else:
        return find_idxSubHandle(pHandle, winClassList[0][0], winClassList[0][1])


def get_hwnd_list():
    """
    获取所有窗口句柄
    """
    hwnd_list = list()

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
    hwnd_list = get_hwnd_list()
    for hwnd in hwnd_list:
        if hwnd.get("title") == name:
            return hwnd["hwnd"]
    else:
        return -1
