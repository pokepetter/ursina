from collections import defaultdict
from enum import Enum



class Keys(Enum):
    left_mouse_down = 'left mouse down'
    left_mouse_up = 'left mouse up'
    middle_mouse_down = 'middle mouse down'
    middle_mouse_up = 'middle mouse up'
    right_mouse_down = 'right mouse down'
    right_mouse_up = 'right mouse up'
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
        # overriden __eq__ to allow for both str and InputEvent comparisons
        if isinstance(other, Keys):
            return self.value == other.value
        return self.value == other



held_keys = defaultdict(lambda: 0)
rebinds = dict()


def bind(original_key, alternative_key):
    rebinds[original_key] = alternative_key
    if ' mouse ' in alternative_key:
        rebinds[original_key + ' up'] = alternative_key[:-5] + ' up'
        return

    rebinds[original_key + ' hold'] = alternative_key + ' hold'
    rebinds[original_key + ' up'] = alternative_key + ' up'


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

    if key.endswith('up'):
        held_keys[key[:-3]] = 0
    else:
        held_keys[key] = 1



if __name__ == '__main__':
    from ursina import *

    app = Ursina()
    input_handler.bind('s', 'arrow down')  # 's'-key will now be registered as 'arrow down'-key

    def test():
        print('----')
    # input_handler.rebind('a', 'f')
    def input(key):
        print(key)
        if key == 'left mouse down':
            print('pressed left mouse button')

        if key == Keys.left_mouse_down:   # same as above, but with Keys enum.
            print('pressed left mouse button')


    def update():
        for key, value in held_keys.items():
            if value != 0:
                print(key, value)



    app.run()
