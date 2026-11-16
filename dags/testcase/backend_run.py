import importlib.util
import os

from gamebot.core.path import PROJECT_ROOT
from gamebot.dag import Group
from gamebot.handlers.packages.win32 import Win32Package


def _load_graph():
    path = os.path.join(PROJECT_ROOT, "dags", "testcase", "_graph.py")
    spec = importlib.util.spec_from_file_location("testcase_graph", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_graph = _load_graph()


def build_setup():
    return {
        "name": "testcase-backend",
        "window": "",
        "packages": _graph.base_packages(Win32Package.install_backend()),
    }


group = Group(name="testcase_backend")
with group as group:
    _graph.build_graph(group)
