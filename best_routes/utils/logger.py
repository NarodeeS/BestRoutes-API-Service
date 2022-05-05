from threading import Thread, Lock
from time import sleep
from .log import Log


class Logger(Thread):
    def __init__(self, interval: int):
        super().__init__()
        self.interval = interval
        self.name = "Logger"
        self.lock = Lock()
        self.logs = []
        self.is_working = True

    def add_log(self, log: Log) -> None:
        self.lock.acquire(blocking=True)
        self.logs.append(log)
        self.lock.release()

    def run(self) -> None:
        while self.is_working:
            self.lock.acquire(blocking=True)
            for log in self.logs:
                print(log)
            self.logs.clear()
            self.lock.release()
            sleep(self.interval)
