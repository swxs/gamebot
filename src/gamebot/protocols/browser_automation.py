from typing import Protocol, runtime_checkable


@runtime_checkable
class BrowserAutomation(Protocol):
    """首期仅契约 stub，实现见后续 playwright_chromium 包。"""

    def goto(self, url: str) -> bool: ...

    def click_selector(self, selector: str) -> bool: ...
