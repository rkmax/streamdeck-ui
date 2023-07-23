import os
import threading
from enum import Enum
from time import sleep, time

from slack import WebClient

from streamdeck_ui.plugins.plugins import BasePlugin

SNOOZE_ICONS = {
    True: os.path.join(os.path.dirname(__file__), 'slack_dnd', 'dnd_on.png'),
    False: os.path.join(os.path.dirname(__file__), 'slack_dnd', 'dnd_off.png')
}
WAIT_ICON = os.path.join(os.path.dirname(__file__), 'slack_dnd', 'wait.gif')


class SlackActions(Enum):
    TOGGLE_DND = 'toggle_dnd'
    TOGGLE_PRESENCE = 'toggle_presence'


class SlackDoNotDisturbPlugin(BasePlugin):
    _in_progress: bool = False
    _snooze_status: bool = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        plugin_config = self.get_plugin_config()
        self.user_id = plugin_config.get('user', None)
        self.token = plugin_config.get('token', None)
        self.action = plugin_config.get('action', SlackActions.TOGGLE_DND)
        self.actions = [
            SlackActions.TOGGLE_DND,
        ]
        self.client = WebClient(token=self.token)
        thead = threading.Thread(target=self._initial_state)
        thead.start()

    def stop(self):
        pass

    def handle_keypress(self, **kwargs):
        if self.action == SlackActions.TOGGLE_DND:
            self._toggle_snooze()
        elif self.action == SlackActions.TOGGLE_PRESENCE:
            pass

    def _initial_state(self) -> None:
        self._in_progress = True
        self._update()
        sleep(1)
        self._get_snooze_status()
        self._in_progress = False
        self._update()

    def _update(self) -> None:
        with self.lock:
            button_state = self.get_button_state()
            if self._in_progress:
                icon = WAIT_ICON
            else:
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
        # status_expiration 60 min from now (epoch time)
        # example 1532627506 is 2018-07-26 15:11:46
        status_expiration = 60 * 60 + int(time())
        self.client.users_profile_set(user=self.user_id, profile={
            'status_text': 'Focused (Do not disturb)',
            'status_emoji': ':no_entry:',
            'status_expiration': status_expiration,
        })

    def _set_away_presence(self) -> None:
        self.client.users_setPresence(user=self.user_id, presence='away')

    def _set_active_presence(self) -> None:
        self.client.users_setPresence(user=self.user_id, presence='auto')

    def _set_available_status(self) -> None:
        self.client.users_profile_set(user=self.user_id, profile={'status_text': '', 'status_emoji': ''})

    def _toggle_snooze(self) -> None:
        if self._in_progress:
            return
        self._in_progress = True
        self._update()
        try:
            if self._get_snooze_status():
                self._disable_dnd_snooze()
                self._set_available_status()
            else:
                self._enable_dnd_snooze()
                self._set_busy_status()
            self._get_snooze_status()
        except Exception as error:
            print(f"Error while toggling snooze: {error}")
        finally:
            self._in_progress = False
            self._update()


def initialize_plugin(**kwargs) -> SlackDoNotDisturbPlugin:
    return SlackDoNotDisturbPlugin(**kwargs)
