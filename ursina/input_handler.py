import sys
from collections import defaultdict
from enum import Enum

control = False
left_control = False
right_control = False

shift = False
left_shift = False
right_shift = False

alt = False
left_alt = False
right_alt = False

held_keys = defaultdict(lambda: 0)
rebinds = dict()


class InputEvents(Enum):
    """ Common mouse events """
    left_mouse_down = 'left mouse down'
    left_mouse_up = 'left mouse up'
    middle_mouse_down = 'middle mouse down'
    middle_mouse_up = 'middle mouse up'
    right_mouse_down = 'right mouse down'
    right_mouse_up = 'right mouse up'
    scroll_up = 'scroll up'
    scroll_down = 'scroll down'
    arrow_left = 'arrow left'
    arrow_left_up = 'arrow left up'
    arrow_up = 'arrow up'
    arrow_up_up = 'arrow up up'
    arrow_down = 'arrow down'
    arrow_down_up = 'arrow down up'
    arrow_right = 'arrow right'
    arrow_right_up = 'arrow right up'
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

    def __eq__(self, other):
        """ Overriden __eq__ to allow for both str and InputEvent comparisions """
        if isinstance(other, InputEvents):
            return self.value == other.value
        return self.value == other


def bind(original_key, alternative_key):
    rebinds[original_key] = alternative_key
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
    if key == InputEvents.arrow_up:
        held_keys[key] = 1
        return
    elif key == InputEvents.arrow_up_up:
        held_keys['arrow up'] = 0
        return

    if key.endswith('up'):
        held_keys[key[:-3]] = 0
    else:
        held_keys[key] = 1


if __name__ == '__main__':
    '''
    key names:
    left mouse down, left mouse up, left mouse hold
    scroll up, scroll down
    arrow left, arrow right, arrow up, arrow down
    space
    '''
    from ursina import *

    app = Ursina()
    input_handler.bind('s', 'arrow down')  # 's'-key will now be registered as 'arrow down'-key

    # input_handler.rebind('a', 'f')
    def input(key):
        print(key)


    # Is there a gamepad connected?
    # from panda3d.core import InputDevice
    # gamepad = None
    # devices = app.devices.getDevices(InputDevice.DeviceClass.gamepad)
    # print( app.devices.getDevices)
    # if devices:
    #     print('gamepads:', devices)
    #     app.connect(devices[0])

    # Accept device dis-/connection events
    # app.accept("connect-device", self.connect)
    # app.accept("disconnect-device", self.disconnect)

    # base.accept("escape", exit)
    #
    # # Accept button events of the first connected gamepad
    # base.accept("gamepad-back", exit)
    # base.accept("gamepad-start", exit)
    # base.accept("gamepad-face_x", self.reset)
    # base.accept("gamepad-face_a", self.action, extraArgs=["face_a"])
    # base.accept("gamepad-face_a-up", self.actionUp)
    # base.accept("gamepad-face_b", self.action, extraArgs=["face_b"])
    # base.accept("gamepad-face_b-up", self.actionUp)
    # base.accept("gamepad-face_y", self.action, extraArgs=["face_y"])
    # base.accept("gamepad-face_y-up", self.actionUp)

    app.run()
