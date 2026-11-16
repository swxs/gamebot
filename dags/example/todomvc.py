"""浏览器示例：在空的 TodoMVC 列表上新增一条「跑通」。不绑定桌面窗口。"""

from gamebot.dag import Group, Node
from gamebot.handlers.packages.playwright import PlaywrightPackage

URL = "https://demo.playwright.dev/todomvc"
ITEM = "跑通"


def build_setup():
    return {
        "name": "TodoMVC",
        "number": 1,
        "packages": {
            "browser": PlaywrightPackage.install_chromium(),
        },
    }


def open_page(ctx):
    return ctx.pkg("browser").goto(URL)


def add_item(ctx):
    browser = ctx.pkg("browser")
    if not browser.fill(".new-todo", ITEM):
        return False
    return browser.press(".new-todo", "Enter")


group = Group(name="todomvc")
with group as group:
    group >> Node("open", open_page) >> Node("add", add_item)
