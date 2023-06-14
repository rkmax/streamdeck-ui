import psutil
from streamdeck_ui.plugins.plugins import BasePlugin
from streamdeck_ui.plugins.utils import TickThread


class CPUPlugin(BasePlugin):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.clock_thread = TickThread(2, self._update_state)

    def start(self):
        self.clock_thread.start()

    def stop(self):
        self.clock_thread.stop()

    def _update_state(self):
        percent = psutil.cpu_percent(interval=1)
        button_state = self.api.get_button_state(self.deck_id, self.page, self.key)
        if button_state['text'] == f"{percent}%":
            return
        button_state['text'] = f"{percent}%"
        self.api.update_button_filter_with_settings(button_state, self.deck_id, self.page, self.key)



def init_state(**kwargs):
    plugin = kwargs.get('plugin', None)
    if plugin is not None:
        return plugin

    clock_plugin = CPUPlugin(**kwargs)
    clock_plugin.start()
    return clock_plugin
