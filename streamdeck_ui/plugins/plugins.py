import runpy
import threading
import traceback
from abc import ABC, abstractmethod
from typing import List

from streamdeck_ui.display.filter import Filter


def prepare_plugin(plugin_path: str, **kwargs):
    api = kwargs.get('api', None)
    deck_id = kwargs.get('deck_id', None)
    page = kwargs.get('page', None)
    key = kwargs.get('key', None)
    if api.plugins[deck_id][page][key] is None:
        try:
            result = runpy.run_path(plugin_path)
            if 'initialize_plugin' in result and callable(result['initialize_plugin']):
                api.plugins[deck_id][page][key] = result['initialize_plugin'](**kwargs)
            elif kwargs.get('non_optional', False):
                print(f"Function initialize_plugin not found in {plugin_path}")
        except Exception as error:
            print(f"Error while calling initialize_plugin in {plugin_path}: {error}")
            traceback.print_exc()
    return api.plugins[deck_id][page][key]


def stop_all_plugins(api, deck_id):
    for page in api.plugins[deck_id]:
        for key in api.plugins[deck_id][page]:
            if api.plugins[deck_id][page][key] is not None:
                api.plugins[deck_id][page][key].stop()
                api.plugins[deck_id][page][key] = None


class BasePlugin(ABC):

    lock: threading.Lock = threading.Lock()

    def __init__(self, **kwargs):
        self.api = kwargs.get("api", None)
        self.page = kwargs.get("page", None)
        self.deck_id = kwargs.get("deck_id", None)
        self.key = kwargs.get("key", None)
        self.filters: List[Filter] = []

    def stop(self, **kwargs):
        self.lock.acquire()
        self.lock.release()

    def get_button_state(self):
        return self.api.get_button_state(self.deck_id, self.page, self.key)

    def get_plugin_config(self):
        return self.api.get_button_plugin_config(self.deck_id, self.page, self.key)

    def synchronize(self, button_state):
        self.api.sync_update_button_filter_with_settings(button_state, self.deck_id, self.page, self.key)

    def handle_keypress(self, **kwargs):
        pass

    def get_filters(self, **kwargs) -> List[Filter]:
        return self.filters
