import os
import re
import subprocess
from typing import List

import psutil

from streamdeck_ui.display.filter import Filter
from streamdeck_ui.plugins.plugins import BasePlugin
from streamdeck_ui.plugins.utils import TickThread

CPU_ICON = os.path.join(os.path.dirname(__file__), 'cpu_plugin', 'cpu.png')
MEM_ICON = os.path.join(os.path.dirname(__file__), 'cpu_plugin', 'mem.png')
GPU_ICON = os.path.join(os.path.dirname(__file__), 'cpu_plugin', 'gpu.png')
STATES = ['cpu', 'mem', 'gpu']
STATES_ICONS = {
    'cpu': CPU_ICON,
    'mem': MEM_ICON,
    'gpu': GPU_ICON
}


def _next_state(current_state: int) -> int:
    if current_state + 1 >= len(STATES):
        return 0
    else:
        return current_state + 1


def _get_gpu_info() -> str:
    output = subprocess.check_output(['nvidia-smi', '--query-gpu=utilization.gpu,temperature.gpu', '--format=csv'])
    output = output.decode('utf-8')
    gpu_stats = re.findall('\d+', output)
    usage = float(gpu_stats[0])
    temperature = float(gpu_stats[1])
    return "{:.1f}%\n\n{:.1f}C".format(usage, temperature)


def _get_cpu_info() -> str:
    usage = psutil.cpu_percent(interval=1)
    temperature = psutil.sensors_temperatures()['coretemp'][0].current
    return "{:.1f}%\n\n{:.1f}C".format(usage, temperature)


def _get_mem_info() -> str:
    total_mem = psutil.virtual_memory().total / 1024 ** 3
    used_mem = psutil.virtual_memory().used / 1024 ** 3
    return "{:.1f}GB\n\n{:.1f}GB".format(used_mem, total_mem)


STATES_INFO = {
    'cpu': _get_cpu_info,
    'mem': _get_mem_info,
    'gpu': _get_gpu_info
}


class CPUPlugin(BasePlugin):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.thread = TickThread(1, self.update)
        self.filters: List[Filter] = []
        self.current_state = 0
        self.thread.start()

    def stop(self):
        self.thread.stop()
        super().stop()

    def handle_keypress(self, **kwargs):
        self.current_state = _next_state(self.current_state)
        self.update()

    def update(self):
        with self.lock:
            button_state = self.get_button_state()
            text = STATES_INFO[STATES[self.current_state]]()
            icon = STATES_ICONS[STATES[self.current_state]]

            if text == button_state['text'] and icon == button_state['icon']:
                return

            button_state['text'] = text
            button_state['icon'] = icon
            self.synchronize(button_state)


def initialize_plugin(**kwargs) -> CPUPlugin:
    return CPUPlugin(**kwargs)
