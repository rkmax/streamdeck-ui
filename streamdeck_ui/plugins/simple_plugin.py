from time import sleep

from streamdeck_ui.plugins.plugins import BasePlugin

lucy = "/home/rkmax/ElGato/Faces/lucy.gif"
power = "/home/rkmax/ElGato/Faces/power_face.gif"


class SimplePlugin(BasePlugin):
    def stop(self):
        pass

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.states = [
            lucy,
            power
        ]
        self.current_state = 0

    def _next_state(self):
        if self.current_state + 1 >= len(self.states):
            return 0
        else:
            return self.current_state + 1

    def handle_keypress(self, **kwargs):
        button_state = self.api.get_button_state(self.deck_id, self.page, self.key)
        next_state = self._next_state()
        button_state['icon'] = self.states[next_state]
        self.current_state = next_state
        sleep(0.04)
        self.api.update_button_filter_with_settings(button_state, self.deck_id, self.page, self.key)


def init_state(**kwargs):
    plugin = kwargs.get('plugin', None)
    if plugin is not None:
        return plugin

    return SimplePlugin(**kwargs)


def handle_keypress(**kwargs):
    plugin = kwargs.get('plugin', None)
    if plugin is not None:
        plugin.handle_keypress(**kwargs)
