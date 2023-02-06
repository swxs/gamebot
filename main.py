import threading

import core
import importlib
from handlers import handler_productor


handler = handler_productor[core.HANDLER]

if core.NAME is None:
    print(f"需要输入名称：")
    exit(1)

hwnd = handler.get_hwnd(core.NAME)

module = importlib.import_module(f'dags.{core.DAG}')
dag = module.dag
dag.setup(handler, hwnd)


class ListenThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.stopped = False
        self.turn = 0

    def run(self):
        while not self.stopped:
            for _ in dag:
                print(_)
                if _ == "end":
                    self.turn += 1
                    print(self.turn)
                    if self.turn == core.NUMBER:
                        self.stopped = True

                if self.stopped:
                    break


def run():
    hThread = ListenThread()
    hThread.start()


if __name__ == "__main__":
    run()
