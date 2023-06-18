import os
import threading

from slack import WebClient

from streamdeck_ui.plugins.plugins import BasePlugin

SNOOZE_ICONS = {
    True:  os.path.join(os.path.dirname(__file__), 'slack_dnd', 'dnd_on.png'),
    False: os.path.join(os.path.dirname(__file__), 'slack_dnd', 'dnd_off.png')
}


class SlackDoNotDisturbPlugin(BasePlugin):
    _in_progress: bool = False
    _snooze_status: bool = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        plugin_config = self.get_plugin_config()
        self.user_id = plugin_config.get('user', None)
        self.token = plugin_config.get('token', None)
        self.client = WebClient(token=self.token)
        thead = threading.Thread(target=self._initial_state)
        thead.start()

    def stop(self):
        pass

    def handle_keypress(self, **kwargs):
        self._toggle_snooze()

    def _initial_state(self) -> None:
        self._get_snooze_status()
        self._update()

    def _update(self) -> None:
        with self.lock:
            button_state = self.get_button_state()
            icon = SNOOZE_ICONS[self._snooze_status]
            if button_state['icon'] != icon:
                button_state['icon'] = icon
                self.synchronize(button_state)

    def _disable_dnd_snooze(self) -> None:
        self.client.dnd_endSnooze(user=self.user_id)

    def _enable_dnd_snooze(self) -> None:
        self.client.dnd_setSnooze(user=self.user_id, num_minutes=60)

    def _get_snooze_status(self) -> bool:
        self._snooze_status = self.client.dnd_info(user=self.user_id)['snooze_enabled']
        return self._snooze_status

    def _set_busy_status(self) -> None:
        self.client.users_profile_set(user=self.user_id, profile={
            'status_text': 'Focused (Do not disturb)',
            'status_emoji': ':no_entry:',
            'status_expiration': 0,
        })

    def _set_available_status(self) -> None:
        self.client.users_profile_set(user=self.user_id, profile={'status_text': '', 'status_emoji': ''})

    def _toggle_snooze(self) -> None:
        if self._in_progress:
            return
        self._in_progress = True
        try:
            if self._get_snooze_status():
                self._disable_dnd_snooze()
                self._set_available_status()
            else:
                self._enable_dnd_snooze()
                self._set_busy_status()
            self._update()
        except Exception as error:
            print(f"Error while toggling snooze: {error}")
        finally:
            self._in_progress = False


def initialize_plugin(**kwargs) -> SlackDoNotDisturbPlugin:
    return SlackDoNotDisturbPlugin(**kwargs)
