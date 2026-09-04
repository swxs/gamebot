from gamebot.handlers.packages._package import Package
from gamebot.handlers.packages.pyauto.pointer_direct import PyAutoPointerDirectHandler


class PyAutoPackage(Package):
    @classmethod
    def check_deps(cls):
        import pyautogui  # noqa: F401

    @classmethod
    def install_pointer_direct(cls):
        return PyAutoPointerDirectHandler()


PyAutoPointerDirectHandler.__package__ = PyAutoPackage
