import importlib.util
import os

from gamebot.core.path import PROJECT_ROOT
from gamebot.dag import Group
from gamebot.handlers.packages.pyauto_desktop import PyAutoDesktopPackage
from gamebot.handlers.packages.win32_window_capture import Win32WindowCapturePackage


def _load_graph():
    path = os.path.join(PROJECT_ROOT, "dags", "testcase", "_graph.py")
    spec = importlib.util.spec_from_file_location("testcase_graph", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_graph = _load_graph()


def build_setup():
    return {
        "packages": _graph.base_packages(
            PyAutoDesktopPackage(),
            Win32WindowCapturePackage.unbound(),
        )
    }


group = Group(name="testcase_pyauto")
with group as group:
    _graph.build_graph(group)
