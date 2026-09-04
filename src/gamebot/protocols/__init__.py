from gamebot.protocols.browser_automation import BrowserAutomation
from gamebot.protocols.clipboard_access import ClipboardAccess
from gamebot.protocols.keyboard_input import KeyboardInput
from gamebot.protocols.pointer_input import PointerInput
from gamebot.protocols.screen_capture import ScreenCapture
from gamebot.protocols.template_matcher import TemplateMatcher
from gamebot.protocols.types import MatchResult, Point, Rect
from gamebot.protocols.window_control import WindowControl

__all__ = [
    "BrowserAutomation",
    "ClipboardAccess",
    "KeyboardInput",
    "MatchResult",
    "PointerInput",
    "Point",
    "Rect",
    "ScreenCapture",
    "TemplateMatcher",
    "WindowControl",
]
