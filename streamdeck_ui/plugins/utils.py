from threading import Thread, Event
from typing import Callable


class TickThread(Thread):
    def __init__(self, tick_time: float, callback: Callable):
        super().__init__()
        self.stop_event = Event()
        self.callback = callback
        self.tick_time = tick_time

    def run(self):
        while not self.stop_event.is_set():
            self.callback()
            self.stop_event.wait(self.tick_time)

    def stop(self):
        self.stop_event.set()
