from time import sleep

from streamdeck_ui.plugins.plugins import BasePlugin

lucy = "/home/rkmax/ElGato/Faces/lucy.gif"
power = "/home/rkmax/ElGato/Faces/power_face.gif"


class SimplePlugin(BasePlugin):

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
        button_state = self.get_button_state()
        next_state = self._next_state()
        button_state['icon'] = self.states[next_state]
        self.current_state = next_state
        sleep(0.04)
        self.synchronize(button_state)


def initialize_plugin(**kwargs) -> SimplePlugin:
    return SimplePlugin(**kwargs)
