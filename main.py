import threading

import core
from handlers import handler_productor
# from dags.Hearthstone_Mercenaries_bot.one_one import dag
from dags.test_bot.run import dag

handler = handler_productor[core.HANDLER]


class ListenThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.stopped = False

    def run(self):
        for _ in dag:
            if _ == "finish":
                print(_)
            if self.stopped:
                break


def run():
    hThread = ListenThread()
    hThread.start()


if __name__ == "__main__":
    hwnd = handler.get_hwnd("Hearthstone")
    dag.setup(handler, hwnd)
    while True:
        for _ in dag:
            if _ == "end":
                print(_)
