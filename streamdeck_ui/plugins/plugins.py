import runpy
from abc import ABC, abstractmethod


def call_plugin_func(plugin_path: str, func_name: str, **kwargs):
    try:
        result = runpy.run_path(plugin_path)
        if func_name in result and callable(result[func_name]):
            return result[func_name](**kwargs)
        elif kwargs.get('non_optional', False):
            print(f"Function {func_name} not found in {plugin_path}")
    except Exception as error:
        print(f"Error while calling {func_name} in {plugin_path}: {error}")


def get_plugin(api, deck_id, page, key):
    return api.plugins[deck_id][page][key]


def set_plugin(api, deck_id, page, key, plugin):
    api.plugins[deck_id][page][key] = plugin


class BasePlugin(ABC):

    @abstractmethod
    def stop(self):
        pass
