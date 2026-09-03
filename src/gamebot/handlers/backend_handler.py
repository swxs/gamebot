import cv2
import random
import win32api
import win32gui
import win32con
import win32ui
from .base_handler import Base

from .utils import hwnd_utils, cv_utils, point_utils

VK_CODE = {}


class BackEnd(Base):
    name = "backend"

    def __init__(self) -> None:
        self.hwnd: int = -1

    def _get_point(self):
        point = win32gui.GetCursorPos()
        window_point = self._get_window_point(self.hwnd, point)
        return window_point

    def start(self, **kwargs):
        self.hwnd = hwnd_utils.get_hwnd_with_name(kwargs.get("name"))
        if self.hwnd == -1:
            raise

    def screen(self, filename):
        # 根据窗口句柄获取窗口的设备上下文DC（Divice Context）
        hwndDC = win32gui.GetWindowDC(self.hwnd)
        # 根据窗口的DC获取mfcDC
        mfcDC = win32ui.CreateDCFromHandle(hwndDC)
        mfcDC_handler = mfcDC.GetHandleAttrib()
        # 截图
        win32gui.SendMessage(
            self.hwnd,
            win32con.WM_PRINT,
            mfcDC_handler,
            win32con.PRF_CLIENT | win32con.PRF_OWNED | win32con.PRF_ERASEBKGND | win32con.PRF_NONCLIENT,
        )
        # mfcDC创建可兼容的DC
        saveDC = mfcDC.CreateCompatibleDC()
        # 创建bigmap准备保存图片
        saveBitMap = win32ui.CreateBitmap()
        # 获取监控器信息
        MoniterDev = win32gui.GetClientRect(self.hwnd)
        # 这个系数是为啥？ 之前也有碰到过
        w = MoniterDev[2] * 3 // 2
        h = MoniterDev[3] * 3 // 2
        # print w,h　　　#图片大小
        # 为bitmap开辟空间
        saveBitMap.CreateCompatibleBitmap(mfcDC, w, h)
        # 高度saveDC，将截图保存到saveBitmap中
        saveDC.SelectObject(saveBitMap)
        # 截取从左上角（0，0）长宽为（w，h）的图片
        saveDC.BitBlt((0, 0), (w, h), mfcDC, (0, 0), win32con.SRCCOPY)
        saveBitMap.SaveBitmapFile(saveDC, filename)
        return cv2.imread(self.hwnd, filename)

    def find_assents(self, total, target_path, sens=0.8):
        target, w, h = cv_utils.get_template_info(target_path)
        loc = cv_utils.diff_image(total, target, sens=sens)
        if len(loc[0]) != 0:
            pt = random.choice(list(zip(*loc[::-1])))
            return (
                point_utils.Point(pt[0], pt[1]),
                point_utils.Point(int((pt[0] * 2 + w) / 2), int((pt[1] * 2 + h) / 2)),
            )
        else:
            return (
                None,
                None,
            )

    def move_to(self, point, speed=0.1, click=True):
        start_point = self._get_point()
        end_point = point

        start_tmp = win32api.MAKELONG(start_point[0], start_point[1])
        end_tmp = win32api.MAKELONG(end_point[0], end_point[1])

        tmp_x = end_point[0] - start_point[0]
        tmp_y = end_point[1] - start_point[1]

        tmp_length = max(abs(tmp_x), abs(tmp_y)) // 10
        if click:
            win32gui.SendMessage(self.hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, start_tmp)
        win32api.SendMessage(self.hwnd, win32con.WM_MOUSEMOVE, 1, start_tmp)
        for i in range(tmp_length):
            current_point = (
                int(start_point[0] + tmp_x / tmp_length * (i + 1)),
                int(start_point[1] + tmp_y / tmp_length * (i + 1)),
            )
            current_tmp = win32api.MAKELONG(current_point[0], current_point[1])
            win32api.SendMessage(self.hwnd, win32con.WM_MOUSEMOVE, 1, current_tmp)
        win32api.SendMessage(self.hwnd, win32con.WM_MOUSEMOVE, 1, end_tmp)
        if click:
            win32gui.SendMessage(self.hwnd, win32con.WM_LBUTTONUP, 0, end_tmp)
        return True

    def left_click_at_point(self, point):
        tmp = win32api.MAKELONG(point.x, point.y)
        win32gui.SendMessage(self.hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, tmp)
        win32gui.SendMessage(self.hwnd, win32con.WM_LBUTTONUP, 0, tmp)
        return True

    def right_click_at_point(self, point):
        tmp = win32api.MAKELONG(point.x, point.y)
        win32gui.SendMessage(self.hwnd, win32con.WM_RBUTTONDOWN, win32con.MK_RBUTTON, tmp)
        win32gui.SendMessage(self.hwnd, win32con.WM_RBUTTONUP, 0, tmp)
        return True

    def keyboard(self, key):
        win32gui.SendMessage(self.hwnd, win32con.WM_KEYDOWN, VK_CODE[key], 0)
        win32gui.SendMessage(self.hwnd, win32con.WM_KEYUP, VK_CODE[key], 0)
        return True
