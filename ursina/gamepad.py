from ursina import *
from panda3d.core import InputDevice

if __name__ == '__main__':
    app = Ursina()
    text_entity = Text()
    player = Entity(model='cube', color=color.azure)

    def update():
        player.x += held_keys['gamepad left stick x'] * time.dt * 5
        player.y += held_keys['gamepad left stick y'] * time.dt * 5
        text_entity.text = '\n'.join([f'{key}: {held_keys[key]}' for key in ('gamepad left trigger', 'gamepad right trigger', 'gamepad right stick x', 'gamepad right stick y')])

    def input(key):
        print('key:', key)

    app.run()



input_handler.gamepad = None
input_handler.gamepads = base.devices.getDevices(InputDevice.DeviceClass.gamepad)
if input_handler.gamepads:
    input_handler.gamepad = input_handler.gamepads[0]


for i, gamepad in enumerate(input_handler.gamepads):
    gamepad_name = 'gamepad'
    if i > 0:
        gamepad_name += f'_{i}'

    base.attachInputDevice(gamepad, prefix=gamepad_name)
    buttons = {
        'face_a' : 'a',
        'face_b' : 'b',
        'face_x' : 'x',
        'face_y' : 'y',
        'lstick' : 'left stick',
        'rstick' : 'right stick',
        'back' : 'back',
        'start' : 'start',
        'dpad_up' : 'dpad up',
        'dpad_down' : 'dpad down',
        'dpad_left' : 'dpad left',
        'dpad_right' : 'dpad right',
        'rshoulder' : 'right shoulder',
        'lshoulder' : 'left shoulder',
    }

    for original_name, new_name in buttons.items():
        base.accept(f'{gamepad_name}-{original_name}', base.input, extraArgs=[f'{gamepad_name} {new_name}'])
        base.accept(f'{gamepad_name}-{original_name}-up', base.input, extraArgs=[f'{gamepad_name} {new_name} up'])
        # print(original_name, new_name)

def update():
    for i, gamepad in enumerate(input_handler.gamepads):
        gamepad_name = 'gamepad'
        if i > 0:
            gamepad_name += f'_{i}'

        # left stick
        x = gamepad.findAxis(InputDevice.Axis.left_x).value
        if abs(x) < .1:
            x = 0
        held_keys[f'{gamepad_name} left stick x'] = x

        y = gamepad.findAxis(InputDevice.Axis.left_y).value
        if abs(y) < .1:
            y = 0
        held_keys[f'{gamepad_name} left stick y'] = y

        # right stick
        x = gamepad.findAxis(InputDevice.Axis.right_x).value
        if abs(x) < .1:
            x = 0
        held_keys[f'{gamepad_name} right stick x'] = x

        y = gamepad.findAxis(InputDevice.Axis.right_y).value
        if abs(y) < .1:
            y = 0
        held_keys[f'{gamepad_name} right stick y'] = y

        held_keys[f'{gamepad_name} left trigger'] = gamepad.findAxis(InputDevice.Axis.left_trigger).value
        held_keys[f'{gamepad_name} right trigger'] = gamepad.findAxis(InputDevice.Axis.right_trigger).value

Entity(name='gamepad_handler', update=update, eternal=True) # connect update() to an entity so it runs
