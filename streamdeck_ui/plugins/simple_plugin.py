from time import sleep

lucy = "/home/rkmax/ElGato/Faces/lucy.gif"
power = "/home/rkmax/ElGato/Faces/power_face.gif"


def init_state(**kwargs):
    return {
        'current_state': 0,
        'states': [
            lucy,
            power
        ]
    }


def _get_next(item_list: list[str], current_index: int) -> int:
    if current_index + 1 >= len(item_list):
        return 0
    else:
        return current_index + 1


def handle_keypress(**kwargs):
    deck_id = kwargs.get("deck_id", None)
    page = kwargs.get("page", None)
    key = kwargs.get("key", None)
    api = kwargs.get("api", None)
    plugin_state = kwargs.get("plugin_state", None)
    plugin_name = kwargs.get("plugin_name", None)
    button_state = api.get_button_state(deck_id, page, key)
    current_state = plugin_state['current_state']
    states = plugin_state['states']
    next_state = _get_next(states, current_state)
    button_state['icon'] = states[next_state]
    plugin_state['current_state'] = next_state
    api.plugins[plugin_name] = plugin_state
    sleep(0.04)
    api.update_button_filter_with_settings(button_state, deck_id, page, key)
