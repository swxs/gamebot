from gamebot.protocols.browser_automation import BrowserAutomation
from gamebot.protocols.clipboard_access import ClipboardAccess
from gamebot.protocols.control_tree import ControlTree
from gamebot.protocols.keyboard_input import KeyboardInput
from gamebot.protocols.pointer_input import PointerInput
from gamebot.protocols.screen_capture import ScreenCapture
from gamebot.protocols.screen_ocr import ScreenOcr
from gamebot.protocols.template_matcher import TemplateMatcher
from gamebot.protocols.types import MatchResult, OcrHit, Point, Rect
from gamebot.protocols.window_control import WindowControl

__all__ = [
    "BrowserAutomation",
    "ClipboardAccess",
    "ControlTree",
    "KeyboardInput",
    "MatchResult",
    "OcrHit",
    "PointerInput",
    "Point",
    "Rect",
    "ScreenCapture",
    "ScreenOcr",
    "TemplateMatcher",
    "WindowControl",
]
