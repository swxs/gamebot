"""共享 testcase 图结构。"""

import os

from gamebot import core
from gamebot.core.path import dag_files_dir
from gamebot.dag import Group, Node
from gamebot.handlers.packages.opencv_matcher import OpenCVMatcherPackage
from gamebot.handlers.packages.pyperclip_pkg import PyperclipPackage


def template_path(name: str) -> str:
    return os.path.join(dag_files_dir("testcase", core.PIX), name)


def bind_window(ctx):
    ctx.pkg("desktop").bind_from_env()
    return True


def click_start(ctx):
    return ctx.pkg("matcher").find_and_click(ctx.pkg("desktop"), template_path("start.png"))


def finish(ctx):
    return True


def build_graph(group: Group):
    bind = Node("bind_window", bind_window)
    start = Node("click_start", click_start)
    end = Node("end", finish)
    group >> bind >> start >> end


def base_packages(desktop):
    return {
        "desktop": desktop,
        "matcher": OpenCVMatcherPackage(),
        "clipboard": PyperclipPackage(),
    }
