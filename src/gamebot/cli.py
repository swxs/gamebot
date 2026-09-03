import importlib.util
import os
import threading

from gamebot import core
from gamebot.core.path import PROJECT_ROOT
from gamebot.handlers import handler_productor


def load_dag_module(dag_spec: str):
    """从 dags/{spec}.py 显式加载用户 DAG 模块，如 testcase.run -> dags/testcase/run.py"""
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
    def __init__(self, group):
        threading.Thread.__init__(self)
        self.group = group
        self.stopped = False
        self.turn = 0

    def run(self):
        while not self.stopped:
            for _ in self.group:
                print(_)
                if _ == "end":
                    self.turn += 1
                    print(self.turn)
                    if self.turn == core.NUMBER:
                        self.stopped = True

                if self.stopped:
                    break


def run():
    handler = handler_productor[core.HANDLER]

    if core.NAME is None:
        print("需要输入名称：")
        exit(1)

    hwnd = handler.get_hwnd(core.NAME)

    module = load_dag_module(core.DAG)
    group = module.group
    group.setup({"handler": handler, "hwnd": hwnd})

    hThread = ListenThread(group)
    hThread.start()


def main():
    run()


if __name__ == "__main__":
    main()
