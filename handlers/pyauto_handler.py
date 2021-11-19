import cv2
import mss
import pyautogui
from .base_handler import Base

class PyAuto(Base):
    __name__ == "pyauto"

    def __init__(self):
        pass

    @classmethod
    def get_point(cls, hwnd):
        return pyautogui.position()

    @classmethod
    def screen(cls, hwnd):
        sct = mss.mss()
        filename = sct.shot(mon=1, output=cls.get_file_path('screen.png'))
        return cv2.imread(cls.get_file_path('screen.png'))

    @classmethod
    def move_to(cls, hwnd, point, speed=0.5):
        return pyautogui.moveTo(point[0], point[1], speed, pyautogui.easeInOutQuad)

    @classmethod
    def left_click_at_point(cls, hwnd, point):
        return pyautogui.click(point[0], point[1])
    
    @classmethod
    def right_click_at_point(cls, hwnd, point):
        return pyautogui.rightClick(point[0], point[1])

