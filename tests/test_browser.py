import numpy as np

from gamebot.handlers.packages.playwright.chromium import PlaywrightChromiumHandler, as_locator


class _Page:
    def __init__(self):
        self.actions = []

    def locator(self, selector):
        return _Locator(self, selector)

    def get_by_role(self, role, name=None):
        return _Locator(self, f"role:{role}:{name}")

    def get_by_text(self, value):
        return _Locator(self, f"text:{value}")

    def screenshot(self):
        return np.zeros((4, 4, 3), dtype=np.uint8)


class _Locator:
    def __init__(self, page, selector):
        self.page = page
        self.selector = selector

    def click(self, timeout=None):
        self.page.actions.append(("click", self.selector, timeout))

    def fill(self, text, timeout=None):
        self.page.actions.append(("fill", self.selector, text))

    def press(self, key, timeout=None):
        self.page.actions.append(("press", self.selector, key))

    def drag_to(self, dest, timeout=None):
        self.page.actions.append(("drag", self.selector, dest.selector))


def test_browser_fill_click_and_role_locator():
    page = _Page()
    handler = PlaywrightChromiumHandler(page=page)
    assert handler.has_page() is True
    assert handler.fill(".new-todo", "跑通") is True
    assert handler.press(".new-todo", "Enter") is True
    assert handler.click({"by": "role", "value": "button", "name": "提交"}) is True
    assert page.actions[0] == ("fill", ".new-todo", "跑通")
    assert page.actions[1][0] == "press"
    assert page.actions[2][1] == "role:button:提交"
    shot = handler.screenshot()
    assert shot.shape == (4, 4, 3)


def test_browser_timeout_is_failure():
    class _SlowPage(_Page):
        def locator(self, selector):
            loc = super().locator(selector)

            def click(timeout=None):
                raise TimeoutError("timed out")

            loc.click = click
            return loc

    handler = PlaywrightChromiumHandler(page=_SlowPage())
    assert handler.click(".missing") is False


def test_as_locator_rejects_unknown_kind():
    page = _Page()
    try:
        as_locator(page, {"by": "xpath", "value": "//a"})
    except ValueError as exc:
        assert "未知定位器" in str(exc)
    else:
        raise AssertionError("expected ValueError")
