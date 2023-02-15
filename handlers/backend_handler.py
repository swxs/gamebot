import win32api
import win32gui
import win32con
import win32ui
from .base_handler import Base

class BackEnd(Base):
    name = "backend"
    
    @classmethod
    def _get_window_point(cls, hwnd, point):
        X1, Y1, X4, Y4 = win32gui.GetWindowRect(hwnd)
        X = point[0] - X1
        Y = point[1] - Y1
        return (X, Y)

    @classmethod
    def get_point(cls, hwnd):
        point = win32gui.GetCursorPos()
        window_point = cls._get_window_point(hwnd, point)
        return window_point
    
    @classmethod
    def move_to(cls, hwnd, point, speed=0.1):
        start_point = cls.get_point(hwnd)
        end_point = point

        end_tmp = win32api.MAKELONG(end_point[0], end_point[1])

        tmp_x = end_point[0] - start_point[0]
        tmp_y = end_point[1] - start_point[1]

        tmp_length = max(abs(tmp_x), abs(tmp_y)) // 10
        win32gui.SendMessage(hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, start_tmp)
        for i in range(tmp_length):
            current_point = (int(start_point[0] + tmp_x / tmp_length * (i + 1)), int(start_point[1] + tmp_y / tmp_length * (i + 1)))
            current_tmp = win32api.MAKELONG(current_point[0], current_point[1])
            win32api.SendMessage(hwnd, win32con.WM_MOUSEMOVE, 1, current_tmp)
        win32api.SendMessage(hwnd, win32con.WM_MOUSEMOVE, 1, end_tmp)
        win32gui.SendMessage(hwnd, win32con.WM_LBUTTONUP, 0, end_tmp)
        return True

    @classmethod
    def left_click_at_point(cls, hwnd, point):
        tmp = win32api.MAKELONG(point[0], point[1])
        win32gui.SendMessage(hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, tmp)
        win32gui.SendMessage(hwnd, win32con.WM_LBUTTONUP, 0, tmp)
        return True
    
    @classmethod
    def right_click_at_point(cls, hwnd, point):
        tmp = win32api.MAKELONG(point[0], point[1])
        win32gui.SendMessage(hwnd, win32con.WM_RBUTTONDOWN, win32con.MK_RBUTTON, tmp)
        win32gui.SendMessage(hwnd, win32con.WM_RBUTTONUP, 0, tmp)
        return True
        
    @classmethod
    def keyboard(cls, hwnd, key):
        win32gui.SendMessage(hwnd, win32con.WM_KEYDOWN, VK_CODE[key], 0)
        win32gui.SendMessage(hwnd, win32con.WM_KEYUP, VK_CODE[key], 0)
        return True
