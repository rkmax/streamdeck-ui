from threading import Thread, Event
from typing import Callable, Union


class TickThread(Thread):
    def __init__(self, tick_time: float, callback: Union[Callable, None] = None):
        super().__init__()
        self.stop_event = Event()
        self.callback = callback
        self.tick_time = tick_time

    def run(self):
        while not self.stop_event.is_set():
            self.execute_callback()
            self.stop_event.wait(self.tick_time)

    def stop(self):
        if self.stop_event.is_set():
            return
        self.stop_event.set()
        try:
            self.join()
        except RuntimeError:
            pass

    def execute_callback(self):
        if self.callback is not None:
            self.callback()

    def it_was_stopped(self):
        return self.stop_event.is_set()
