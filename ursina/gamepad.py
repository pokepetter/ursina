from ursina import input_handler, held_keys, Entity
from panda3d.core import InputDevice, InputDeviceManager

main_gamepad_index = 0


if __name__ == '__main__':
    from ursina import Ursina, Text, time, color, window
    app = Ursina()
    window.color = color.black


# input_handler.gamepad = None
input_handler.gamepads = base.devices.getDevices(InputDevice.DeviceClass.gamepad)
if input_handler.gamepads:
    input_handler.gamepad = input_handler.gamepads[0]

# def disconnect_all():

def connect_all():
    for i, gamepad in enumerate(input_handler.gamepads):
        try:
            base.detachInputDevice(gamepad)
        except:
            pass

    for i, gamepad in enumerate(input_handler.gamepads):
        gamepad_name = 'gamepad'
        if i != main_gamepad_index:
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
        if i != main_gamepad_index:
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
connect_all()


if __name__ == '__main__':
    text_entity = Text()
    print('---------------', input_handler.gamepads)
    print('---------------', input_handler.gamepad)
    [print('-----------', gamepad) for gamepad in input_handler.gamepads]
    gamepad_list = Text('\n'.join([f'{i}) {gamepad}' for i, gamepad in enumerate(input_handler.gamepads)]), x=-.5, y=.3)
    player = Entity(model='cube', color=color.azure)

    def update():
        player.x += held_keys['gamepad left stick x'] * time.dt * 5
        player.y += held_keys['gamepad left stick y'] * time.dt * 5
        text_entity.text = '\n'.join([f'{key}: {held_keys[key]}' for key in ('gamepad left trigger', 'gamepad right trigger', 'gamepad right stick x', 'gamepad right stick y')])

    def input(key):
        global main_gamepad_index
        print('key:', key)
        if key.isdigit():
            i = int(key)
            if i < len(input_handler.gamepads):
                print('set main gamepad to:', input_handler.gamepads[i])
                main_gamepad_index = i
                connect_all()
                # input_handler.gamepads = [target_gamepad, ] + input_handler.gamepads
                # target_gamepad = input_handler.gamepads.pop(i)
                # input_handler.gamepad = input_handler.gamepads[i]


    app.run()
