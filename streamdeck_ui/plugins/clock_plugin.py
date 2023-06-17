from datetime import datetime

from streamdeck_ui.plugins.plugins import BasePlugin
from streamdeck_ui.plugins.utils import TickThread


class ClockPlugin(BasePlugin):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.clock_thread = TickThread(10, self._update_state)
        self.clock_thread.start()

    def stop(self):
        self.clock_thread.stop()
        super().stop()

    def _update_state(self):
        current_time = datetime.now().strftime('%H:%M')
        button_state = self.get_button_state()
        if current_time == button_state['text']:
            return
        button_state['text'] = current_time
        self.synchronize(button_state)


def initialize_plugin(**kwargs) -> ClockPlugin:
    return ClockPlugin(**kwargs)
