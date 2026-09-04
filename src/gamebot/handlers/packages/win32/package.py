from gamebot.handlers.packages._package import Package
from gamebot.handlers.packages.win32.backend import Win32BackendHandler
from gamebot.handlers.packages.win32.capture import Win32CaptureHandler


class Win32Package(Package):
    @classmethod
    def check_deps(cls):
        import win32api  # noqa: F401
        import win32con  # noqa: F401
        import win32gui  # noqa: F401
        import win32ui  # noqa: F401

    @classmethod
    def install_backend(cls):
        return Win32BackendHandler.unbound()

    @classmethod
    def install_capture(cls):
        return Win32CaptureHandler.unbound()


Win32BackendHandler.__package__ = Win32Package
Win32CaptureHandler.__package__ = Win32Package
