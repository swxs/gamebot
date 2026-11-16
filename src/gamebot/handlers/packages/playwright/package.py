from gamebot.handlers.packages._package import Package
from gamebot.handlers.packages.playwright.chromium import PlaywrightChromiumHandler


class PlaywrightPackage(Package):
    @classmethod
    def check_deps(cls):
        import playwright  # noqa: F401

    @classmethod
    def install_chromium(cls):
        return PlaywrightChromiumHandler()


PlaywrightChromiumHandler.__package__ = PlaywrightPackage
