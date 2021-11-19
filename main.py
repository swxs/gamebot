import threading

import core
from handlers import handler_productor
from dags import dag_productor


handler = handler_productor[core.HANDLER]
dag = dag_productor[core.DAG]

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
    run()
