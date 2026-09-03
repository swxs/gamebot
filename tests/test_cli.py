import os

import pytest

from gamebot.cli import load_dag_module
from gamebot.core.path import PROJECT_ROOT


def test_load_dag_module_path_convention():
    parts = ["testcase", "run"]
    expected = os.path.join(PROJECT_ROOT, "dags", *parts[:-1], parts[-1] + ".py")
    assert expected.replace("\\", "/").endswith("dags/testcase/run.py")


def test_load_dag_module_raises_for_missing():
    with pytest.raises(FileNotFoundError):
        load_dag_module("nonexistent.module")


def test_load_dag_module_minimal(tmp_path, monkeypatch):
    dag_file = tmp_path / "sample.py"
    dag_file.write_text(
        "from gamebot.dag import Group\n"
        "group = Group(name='sample')\n",
        encoding="utf-8",
    )

    def fake_join(root, *parts):
        if parts[:1] == ("dags",):
            return str(dag_file)
        return os.path.join(root, *parts)

    monkeypatch.setattr("gamebot.cli.os.path.join", fake_join)
    module = load_dag_module("sample.run")
    assert module.group.name == "sample"
