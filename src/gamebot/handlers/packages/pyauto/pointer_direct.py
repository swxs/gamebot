import pyautogui

from gamebot.protocols.types import Point


class PyAutoPointerDirectHandler:
    def __init__(self):
        # 四角失败保护只覆盖真实光标。SendMessage 路径不经过这里。
        pyautogui.FAILSAFE = True

    def move_to(self, point: Point, duration: float = 0.5):
        pyautogui.moveTo(point.x, point.y, duration=duration, tween=pyautogui.easeInOutQuad)
        return True

    def click(self, point: Point):
        pyautogui.click(point.x, point.y)
        return True

    def double_click(self, point: Point):
        pyautogui.doubleClick(point.x, point.y)
        return True

    def right_click(self, point: Point):
        pyautogui.rightClick(point.x, point.y)
        return True

    def drag(self, start: Point, end: Point, duration: float = 0.2):
        pyautogui.moveTo(start.x, start.y)
        pyautogui.dragTo(end.x, end.y, duration=duration, button="left")
        return True

    def scroll(self, point: Point, clicks: int):
        pyautogui.scroll(clicks, x=point.x, y=point.y)
        return True

    def press(self, key: str):
        pyautogui.press(key)
        return True

    def type_text(self, text: str):
        pyautogui.typewrite(text, interval=0.05)
        return True

    def hotkey(self, *keys: str):
        pyautogui.hotkey(*keys)
        return True
