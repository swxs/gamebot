import cv2
import mss
import pyautogui
from .base_handler import Base


class PyAuto(Base):
    name = "pyauto"

    def get_point(self):
        return pyautogui.position()

    def screen(self, filename):
        return cv2.imread(mss.mss().shot(mon=1, output=filename))

    def move_to(self, point, duration=0.5):
        return pyautogui.moveTo(point.x, point.y, duration=duration, tween=pyautogui.easeInOutQuad)

    def left_click_at_point(self, point):
        return pyautogui.click(point.x, point.y)

    def right_click_at_point(self, point):
        return pyautogui.rightClick(point.x, point.y)
