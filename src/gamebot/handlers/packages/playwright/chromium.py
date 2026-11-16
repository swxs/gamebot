"""Playwright Chromium。定位器可以是选择器字符串，或 {by, value, name?}。"""

import numpy as np


_BY = {
    "role": "get_by_role",
    "text": "get_by_text",
    "label": "get_by_label",
    "placeholder": "get_by_placeholder",
    "alt": "get_by_alt_text",
    "title": "get_by_title",
    "test_id": "get_by_test_id",
    "css": "locator",
}


def as_locator(page, spec):
    if isinstance(spec, str):
        return page.locator(spec)
    if not isinstance(spec, dict) or "by" not in spec:
        raise ValueError("locator 必须是选择器字符串，或 {by, value}")
    kind = spec["by"]
    if kind not in _BY:
        raise ValueError(f"未知定位器: {kind}")
    value = spec.get("value", "")
    method = getattr(page, _BY[kind])
    if kind == "role" and spec.get("name"):
        return method(value, name=spec["name"])
    return method(value)


def timeout_ms(timeout: float) -> int:
    return int(timeout * 1000)


class PlaywrightChromiumHandler:
    def __init__(self, page=None):
        self._page = page
        self._playwright = None
        self._browser = None
        self._context = None

    def has_page(self) -> bool:
        return self._page is not None

    def _ensure(self):
        if self._page is not None:
            return self._page
        from playwright.sync_api import sync_playwright

        self._playwright = sync_playwright().start()
        self._browser = self._playwright.chromium.launch(headless=False)
        self._context = self._browser.new_context()
        self._page = self._context.new_page()
        return self._page

    def _ok(self, action) -> bool:
        try:
            action()
            return True
        except Exception as exc:
            if isinstance(exc, AssertionError) or type(exc).__name__ == "TimeoutError":
                return False
            raise

    def goto(self, url: str, timeout: float = 10) -> bool:
        page = self._ensure()
        return self._ok(lambda: page.goto(url, timeout=timeout_ms(timeout)))

    def click(self, locator, timeout: float = 10) -> bool:
        page = self._ensure()
        target = as_locator(page, locator)
        return self._ok(lambda: target.click(timeout=timeout_ms(timeout)))

    def click_selector(self, selector: str, timeout: float = 10) -> bool:
        return self.click(selector, timeout=timeout)

    def fill(self, locator, text: str, timeout: float = 10) -> bool:
        page = self._ensure()
        target = as_locator(page, locator)
        return self._ok(lambda: target.fill(text, timeout=timeout_ms(timeout)))

    def press(self, locator, key: str, timeout: float = 10) -> bool:
        page = self._ensure()
        target = as_locator(page, locator)
        return self._ok(lambda: target.press(key, timeout=timeout_ms(timeout)))

    def drag(self, source, target, timeout: float = 10) -> bool:
        page = self._ensure()
        origin = as_locator(page, source)
        dest = as_locator(page, target)
        return self._ok(lambda: origin.drag_to(dest, timeout=timeout_ms(timeout)))

    def expect(self, locator, text: str | None = None, timeout: float = 10) -> bool:
        from playwright.sync_api import expect as playwright_expect

        page = self._ensure()
        target = as_locator(page, locator)

        def check():
            assertion = playwright_expect(target)
            if text is None:
                assertion.to_be_visible(timeout=timeout_ms(timeout))
            else:
                assertion.to_have_text(text, timeout=timeout_ms(timeout))

        return self._ok(check)

    def start_trace(self) -> bool:
        self._ensure()
        if self._context is None:
            return False
        self._context.tracing.start(screenshots=True, snapshots=True)
        return True

    def stop_trace(self, path: str) -> bool:
        if self._context is None:
            return False
        self._context.tracing.stop(path=path)
        return True

    def screenshot(self):
        if self._page is None:
            return None
        raw = self._page.screenshot()
        if isinstance(raw, np.ndarray):
            return raw
        if not raw:
            return None
        import cv2

        array = np.frombuffer(raw, dtype=np.uint8)
        return cv2.imdecode(array, cv2.IMREAD_COLOR)
