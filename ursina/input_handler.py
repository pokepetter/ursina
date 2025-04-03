"""
ursina/input_handler.py

This module handles input events and key bindings for the Ursina engine.
It provides functionality for managing key states, rebinding keys, and handling input events.
"""

from collections import defaultdict
from enum import Enum


class Keys(Enum):
    """
    Enum class representing various input keys and events.
    """
    left_mouse_down = 'left mouse down'
    left_mouse_up = 'left mouse up'
    middle_mouse_down = 'middle mouse down'
    middle_mouse_up = 'middle mouse up'
    right_mouse_down = 'right mouse down'
    right_mouse_up = 'right mouse up'
    double_click = 'double click'
    scroll_up = 'scroll up'
    scroll_down = 'scroll down'
    left_arrow = 'left arrow'
    left_arrow_up = 'left arrow up'
    up_arrow = 'up arrow'
    up_arrow_up = 'up arrow up'
    down_arrow = 'down arrow'
    down_arrow_up = 'down arrow up'
    right_arrow = 'right arrow'
    right_arrow_up = 'right arrow up'
    left_control = 'left control'
    right_control = 'right control'
    left_shift = 'left shift'
    right_shift = 'right shift'
    left_alt = 'left alt'
    right_alt = 'right alt'
    left_control_up = 'left control up'
    right_control_up = 'right control up'
    left_shift_up = 'left shift up'
    right_shift_up = 'right shift up'
    left_alt_up = 'left alt up'
    right_alt_up = 'right alt up'
    page_down = 'page down'
    page_down_up = 'page down up'
    page_up = 'page up'
    page_up_up = 'page up up'
    enter = 'enter'
    backspace = 'backspace'
    escape = 'escape'
    tab = 'tab'

    gamepad_left_stick_x = 'gamepad left stick x'   # held_keys only
    gamepad_left_stick_y = 'gamepad left stick y'   # held_keys only
    gamepad_right_stick_x = 'gamepad right stick x'   # held_keys only
    gamepad_right_stick_y = 'gamepad right stick y'   # held_keys only
    gamepad_left_trigger = 'gamepad left trigger'   # held_keys only
    gamepad_right_trigger = 'gamepad right trigger'   # held_keys only
    gamepad_a = 'gamepad a'
    gamepad_a_up = 'gamepad a up'
    gamepad_b = 'gamepad b'
    gamepad_b_up = 'gamepad b up'
    gamepad_x = 'gamepad x'
    gamepad_x_up = 'gamepad x up'
    gamepad_y = 'gamepad y'
    gamepad_y_up = 'gamepad y up'
    gamepad_left_stick = 'gamepad left stick'
    gamepad_left_stick_up = 'gamepad left stick up'
    gamepad_right_stick = 'gamepad right stick'
    gamepad_right_stick_up = 'gamepad right stick up'
    gamepad_back = 'gamepad back'
    gamepad_back_up = 'gamepad back up'
    gamepad_start = 'gamepad start'
    gamepad_dpad_down = 'gamepad dpad down'
    gamepad_dpad_down_up = 'gamepad dpad down up'
    gamepad_dpad_up = 'gamepad dpad up'
    gamepad_dpad_up_up = 'gamepad dpad up up'
    gamepad_dpad_left = 'gamepad dpad left'
    gamepad_dpad_left_up = 'gamepad dpad left up'
    gamepad_dpad_right = 'gamepad dpad right'
    gamepad_dpad_right_up = 'gamepad dpad right up'
    gamepad_left_shoulder = 'gamepad left shoulder'
    gamepad_left_shoulder_up = 'gamepad left shoulder up'
    gamepad_right_shoulder = 'gamepad right shoulder'
    gamepad_right_shoulder_up = 'gamepad right shoulder up'

    def __hash__(self):
        """
        Override the hash method to use the value of the enum.
        """
        return hash(self.value)

    def __eq__(self, other):
        """
        Override the equality method to allow for both str and InputEvent comparisons.
        """
        if isinstance(other, Keys):
            return self.value == other.value
        return self.value == other


# Dictionary to keep track of held keys and their states
held_keys = defaultdict(lambda: 0)
# Dictionary to store key rebindings
rebinds = dict()


def bind(original_key, alternative_key):
    """
    Bind an alternative key to an original key.

    Args:
        original_key (str): The original key to bind.
        alternative_key (str): The alternative key to bind to the original key.
    """
    if not original_key in rebinds:
        rebinds[original_key] = {original_key, }

    rebinds[original_key].add(alternative_key)

    if ' mouse ' in alternative_key:
        if not rebinds.get(f'{original_key} up'):
            rebinds[f'{original_key} up'] = {original_key, }
        rebinds[f'{original_key} up'].add(f'{alternative_key[:-5]} up')
        return

    if not rebinds.get(f'{original_key} hold'):
        rebinds[f'{original_key} hold'] = {f'{original_key} hold', }
    rebinds[f'{original_key} hold'].add(f'{alternative_key} hold')

    if not rebinds.get(f'{original_key} up'):
        rebinds[f'{original_key} up'] = {f'{original_key} up', }
    rebinds[f'{original_key} up'].add(f'{alternative_key} up')


def unbind(key):
    """
    Unbind a key and its associated bindings.

    Args:
        key (str): The key to unbind.
    """
    if key in rebinds:
        del rebinds[key]
        del rebinds[key + ' hold']
        del rebinds[key + ' up']
    else:
        rebinds[key] = 'none'


def rebind(to_key, from_key):
    """
    Rebind a key to another key.

    Args:
        to_key (str): The key to rebind.
        from_key (str): The key to bind to.
    """
    unbind(to_key)
    bind(to_key, from_key)


def input(key):
    """
    Handle input events and update the held_keys dictionary.

    Args:
        key (str): The input key.
    """
    if key.endswith('hold') or key == Keys.scroll_down or key == Keys.scroll_up:
        return

    key = key.replace('mouse down', 'mouse')

    if key.endswith(' up') and key != 'page up' and key != 'gamepad dpad up':
        held_keys[key[:-3]] = 0
    else:
        held_keys[key] = 1


def get_combined_key(key):
    """
    Add control, shift, and alt prefix to the key.

    Args:
        key (str): The input key.

    Returns:
        str: The combined key with prefixes.
    """
    return ''.join(e+'+' for e in ('control', 'shift', 'alt') if held_keys[e] and not e == key) + key


if __name__ == '__main__':
    from ursina import *
    from ursina import Ursina, input_handler

    app = Ursina(borderless=False)
    input_handler.bind('z', 'w')  # 'z'-key will now be registered as 'w'-key
    input_handler.bind('left mouse down', 'attack')  # 'left mouse down'-key will now send 'attack'to input functions
    input_handler.bind('gamepad b', 'attack')  # 'gamepad b'-key will now be registered as 'attack'-key

    def input(key):
        print('got key:', key)
        if key == 'attack':
            destroy(Entity(model='cube', color=color.blue), delay=.2)

    app.run()
