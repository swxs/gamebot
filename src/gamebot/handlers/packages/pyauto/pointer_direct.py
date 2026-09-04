import pyautogui

from gamebot.protocols.types import Point


class PyAutoPointerDirectHandler:

    def move_to(self, point: Point, duration: float = 0.5):
        pyautogui.moveTo(point.x, point.y, duration=duration, tween=pyautogui.easeInOutQuad)
        return True

    def click(self, point: Point):
        pyautogui.click(point.x, point.y)
        return True

    def right_click(self, point: Point):
        pyautogui.rightClick(point.x, point.y)
        return True

    def press(self, key: str):
        pyautogui.press(key)
        return True

    def type_text(self, text: str):
        pyautogui.typewrite(text, interval=0.05)
        return True
