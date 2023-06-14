from datetime import datetime

from streamdeck_ui.plugins.plugins import BasePlugin
from streamdeck_ui.plugins.utils import TickThread


class ClockPlugin(BasePlugin):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.clock_thread = TickThread(1, self._update_state)

    def start(self):
        self.clock_thread.start()

    def stop(self):
        self.clock_thread.stop()

    def _update_state(self):
        current_time = datetime.now().strftime('%H:%M')
        button_state = self.api.get_button_state(self.deck_id, self.page, self.key)
        if button_state['text'] == current_time:
            return
        button_state['text'] = current_time
        self.api.update_button_filter_with_settings(button_state, self.deck_id, self.page, self.key)


def init_state(**kwargs):
    plugin = kwargs.get('plugin', None)
    if plugin is not None:
        return plugin

    clock_plugin = ClockPlugin(**kwargs)
    clock_plugin.start()
    return clock_plugin
