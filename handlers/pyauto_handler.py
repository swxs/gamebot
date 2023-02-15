import cv2
import mss
import pyautogui
from .base_handler import Base


class PyAuto(Base):
    name = "pyauto"

    @classmethod
    def get_point(cls, hwnd):
        return pyautogui.position()

    @classmethod
    def screen(cls, hwnd, filename):
        return cv2.imread(mss.mss().shot(mon=1, output=filename))

    @classmethod
    def move_to(cls, hwnd, point, speed=0.5):
        return pyautogui.moveTo(point[0], point[1], speed, pyautogui.easeInOutQuad)

    @classmethod
    def left_click_at_point(cls, hwnd, point):
        return pyautogui.click(point[0], point[1])

    @classmethod
    def right_click_at_point(cls, hwnd, point):
        return pyautogui.rightClick(point[0], point[1])
