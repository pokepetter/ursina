from collections import defaultdict
from enum import Enum


class Keys(Enum):
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
        return hash(self.value)

    def __eq__(self, other):
        # overridden __eq__ to allow for both str and InputEvent comparisons
        if isinstance(other, Keys):
            return self.value == other.value
        return self.value == other



held_keys = defaultdict(lambda: 0)
rebinds = dict()


def bind(original_key, alternative_key):
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

    # rebinds[original_key + ' hold'] = alternative_key + ' hold'
    # rebinds[original_key + ' up'] = alternative_key + ' up'

def unbind(key):
    if key in rebinds:
        del rebinds[key]
        del rebinds[key + ' hold']
        del rebinds[key + ' up']
    else:
        rebinds[key] = 'none'


def rebind(to_key, from_key):
    unbind(to_key)
    bind(to_key, from_key)


def input(key):
    if key.endswith('hold') or key == Keys.scroll_down or key == Keys.scroll_up:
        return

    key = key.replace('mouse down', 'mouse')

    if key.endswith(' up') and key != 'page up' and key != 'gamepad dpad up':
        held_keys[key[:-3]] = 0
    else:
        held_keys[key] = 1


def get_combined_key(key):
    '''
    Adds control, shift and alt prefix to key.
    Example: holding control and pressing 'f' would result in 'control+f'.
    This makes it easier to check for a specific combination without manually
    checking each combination of held_keys['control'], held_keys['shift'] and held_keys['alt'].
    '''

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
        # if key == 'left mouse down':
        #     print('pressed left mouse button')

        # if key == Keys.left_mouse_down:   # same as above, but with Keys enum.
        #     print('pressed left mouse button')


    # def update():
    #     for key, value in held_keys.items():
    #         if value != 0:
    #             print(key, value)



    app.run()
