from gamebot.handlers.packages._package import Package
from gamebot.handlers.packages.pyperclip.clipboard import PyperclipHandler


class PyperclipPackage(Package):
    @classmethod
    def check_deps(cls):
        import pyperclip  # noqa: F401

    @classmethod
    def install_clipboard(cls):
        return PyperclipHandler()


PyperclipHandler.__package__ = PyperclipPackage
