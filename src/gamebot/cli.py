import importlib.util
import os
import sys
import threading
import webbrowser

from gamebot.core.config import SetupError, resolve_setup
from gamebot.core.evidence import EvidenceWriter
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
        safe = "".join(ch if ch not in '<>:"/\\|?*' else "_" for ch in (group.get("name") or "run"))
        self.evidence = EvidenceWriter(os.path.join(PROJECT_ROOT, "runs", safe))

    def run(self):
        number = self.group.get("number")
        while not self.stopped:
            for step in self.group:
                print(step)
                self.evidence.write(self.group, step)
                self.hub.publish(build_snapshot(self.group, turn=self.turn))
                if self.stopped:
                    break
            if self.stopped:
                break
            self.turn += 1
            print(self.turn)
            if self.turn == number:
                self.stopped = True


def run(dag_spec: str):
    module = load_dag_module(dag_spec)
    if not hasattr(module, "build_setup"):
        raise AttributeError(f"DAG module {dag_spec!r} must export build_setup()")

    setup = resolve_setup(module.build_setup(), dag_spec)
    group = module.group
    group.setup(setup)

    hub = StateHub()
    graph = serialize_graph(group)
    port = group.get("dashboard_port")
    url = start_dashboard(hub, graph, port=port)
    print(f"dashboard: {url}")
    if group.get("dashboard_open"):
        webbrowser.open(url)

    hub.publish(build_snapshot(group, turn=0))

    thread = ListenThread(group, hub)
    thread.start()
    thread.join()


def main(argv=None):
    args = list(sys.argv[1:] if argv is None else argv)
    if len(args) != 1:
        print("用法: gamebot <模块路径>", file=sys.stderr)
        raise SystemExit(2)
    try:
        run(args[0])
    except SetupError as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(2)


if __name__ == "__main__":
    main()
