"""共享 testcase 图结构。"""

import os

from gamebot.core.path import dag_files_dir
from gamebot.dag import Group, Node
from gamebot.handlers.packages.opencv import OpenCVPackage
from gamebot.handlers.packages.pyperclip import PyperclipPackage


def template_path(ctx, name: str) -> str:
    return os.path.join(dag_files_dir("testcase", ctx.get("pix") or ""), name)


def bind_window(ctx):
    title = ctx.get("window") or ""
    if not title:
        return False
    try:
        target = ctx.pkg("capture")
    except KeyError:
        target = ctx.pkg("desktop")
    target.bind_title(title)
    return True


def click_start(ctx):
    matcher = ctx.pkg("matcher")
    path = template_path(ctx, "start.png")
    try:
        return matcher.find_and_click(ctx.pkg("capture"), ctx.pkg("desktop"), path)
    except KeyError:
        desktop = ctx.pkg("desktop")
        return matcher.find_and_click(desktop, desktop, path)


def finish(ctx):
    return True


def build_graph(group: Group):
    bind = Node("bind_window", bind_window)
    start = Node("click_start", click_start)
    end = Node("end", finish)
    group >> bind >> start >> end


def base_packages(desktop, capture=None):
    packages = {
        "desktop": desktop,
        "matcher": OpenCVPackage.install_matcher(),
        "clipboard": PyperclipPackage.install_clipboard(),
    }
    if capture is not None:
        packages["capture"] = capture
    return packages
