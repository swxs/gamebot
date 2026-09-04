import importlib.util
import os
import threading
import webbrowser

from gamebot import core
from gamebot.core.path import PROJECT_ROOT
from gamebot.dashboard import StateHub, build_snapshot, serialize_graph, start_dashboard


def load_dag_module(dag_spec: str):
    """从 dags/{spec}.py 显式加载用户 DAG 模块，如 testcase.pyauto_run -> dags/testcase/pyauto_run.py"""
    parts = dag_spec.split(".")
    file_path = os.path.join(PROJECT_ROOT, "dags", *parts[:-1], parts[-1] + ".py")
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"DAG file not found: {file_path}")

    module_name = "_gamebot_user_dag_" + dag_spec.replace(".", "_")
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ListenThread(threading.Thread):
    def __init__(self, group, hub: StateHub):
        threading.Thread.__init__(self)
        self.group = group
        self.hub = hub
        self.stopped = False
        self.turn = 0

    def run(self):
        while not self.stopped:
            for step in self.group:
                print(step)
                self.hub.publish(build_snapshot(self.group, turn=self.turn))
                if step == "end":
                    self.turn += 1
                    print(self.turn)
                    if self.turn == core.NUMBER:
                        self.stopped = True

                if self.stopped:
                    break


def run():
    module = load_dag_module(core.DAG)
    if not hasattr(module, "build_setup"):
        raise AttributeError(f"DAG module {core.DAG!r} must export build_setup()")

    group = module.group
    group.setup(module.build_setup())

    hub = StateHub()
    graph = serialize_graph(group)
    url = start_dashboard(hub, graph, port=core.DASHBOARD_PORT)
    print(f"dashboard: {url}")
    if core.DASHBOARD_OPEN:
        webbrowser.open(url)

    hub.publish(build_snapshot(group, turn=0))

    hThread = ListenThread(group, hub)
    hThread.start()
    hThread.join()


def main():
    run()


if __name__ == "__main__":
    main()
