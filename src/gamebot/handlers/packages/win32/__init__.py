from gamebot.handlers.packages.win32.backend import Win32BackendHandler
from gamebot.handlers.packages.win32.capture import Win32CaptureHandler
from gamebot.handlers.packages.win32.package import Win32Package

Win32BackendPackage = Win32BackendHandler
Win32WindowCapturePackage = Win32CaptureHandler

__all__ = [
    "Win32Package",
    "Win32BackendHandler",
    "Win32CaptureHandler",
    "Win32BackendPackage",
    "Win32WindowCapturePackage",
]
