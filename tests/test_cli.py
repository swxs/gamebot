import os

import pytest

from gamebot.cli import load_dag_module
from gamebot.core.path import PROJECT_ROOT


def test_load_dag_module_path_convention():
    parts = ["testcase", "pyauto_run"]
    expected = os.path.join(PROJECT_ROOT, "dags", *parts[:-1], parts[-1] + ".py")
    assert expected.replace("\\", "/").endswith("dags/testcase/pyauto_run.py")


def test_load_dag_module_raises_for_missing():
    with pytest.raises(FileNotFoundError):
        load_dag_module("nonexistent.module")


def test_load_dag_module_minimal(tmp_path, monkeypatch):
    dag_file = tmp_path / "sample.py"
    dag_file.write_text(
        "from gamebot.dag import Group\n"
        "group = Group(name='sample')\n"
        "def build_setup():\n"
        "    return {}\n",
        encoding="utf-8",
    )

    def fake_join(root, *parts):
        if parts[:1] == ("dags",):
            return str(dag_file)
        return os.path.join(root, *parts)

    monkeypatch.setattr("gamebot.cli.os.path.join", fake_join)
    module = load_dag_module("sample.run")
    assert module.group.name == "sample"
    assert module.build_setup() == {}


def test_run_requires_build_setup(monkeypatch):
    from gamebot.dag import Group

    class FakeModule:
        group = Group(name="x")

    monkeypatch.setattr("gamebot.cli.load_dag_module", lambda spec: FakeModule())

    from gamebot.cli import run

    with pytest.raises(AttributeError, match="build_setup"):
        run("sample.run")


def test_resolve_setup_defaults_and_rejects():
    from gamebot.core.config import SetupError, resolve_setup

    resolved = resolve_setup({"name": "TodoMVC", "packages": {}}, "example.todomvc")
    assert resolved["name"] == "TodoMVC"
    assert resolved["number"] == 1
    assert resolved["pix"] == ""
    assert resolved["dashboard_port"] == 8765
    assert resolved["dashboard_open"] is False
    assert resolved["dag"] == "example.todomvc"

    with pytest.raises(SetupError, match="name"):
        resolve_setup({}, "example.todomvc")
    with pytest.raises(SetupError, match="number"):
        resolve_setup({"name": "n", "number": 0}, "example.todomvc")


def test_main_requires_one_module_path():
    from gamebot.cli import main

    with pytest.raises(SystemExit) as exc:
        main([])
    assert exc.value.code == 2


def test_listen_stops_after_one_pass_without_end_node():
    from gamebot.cli import ListenThread
    from gamebot.core.config import resolve_setup
    from gamebot.dag import Group, Node
    from gamebot.dashboard import StateHub

    group = Group(name="g")
    with group as group:
        group >> Node("work", lambda ctx: True)
    group.setup(resolve_setup({"name": "listen-once"}, "example.once"))
    thread = ListenThread(group, StateHub())
    thread.evidence = type("W", (), {"write": lambda self, group, step: None})()
    thread.run()
    assert thread.turn == 1
