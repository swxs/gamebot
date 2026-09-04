from gamebot.handlers.packages._package import Package
from gamebot.handlers.packages.opencv.matcher import OpenCVMatcherHandler


class OpenCVPackage(Package):
    @classmethod
    def check_deps(cls):
        import cv2  # noqa: F401
        import numpy  # noqa: F401

    @classmethod
    def install_matcher(cls):
        return OpenCVMatcherHandler()


OpenCVMatcherHandler.__package__ = OpenCVPackage
