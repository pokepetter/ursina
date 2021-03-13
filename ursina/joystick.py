from ursina import *
from panda3d.core import InputDevice

if __name__ == '__main__':
    app = Ursina()
    text_entity = Text()
    player = Entity(model='cube', color=color.azure)

    def update():
        player.x += held_keys['joystick x'] * time.dt * 5
        player.y += held_keys['joystick y'] * time.dt * 5
        text_entity.text = '\n'.join([f'{key}: {held_keys[key]}' for key in ('gamepad left trigger', 'gamepad right trigger', 'gamepad right stick x', 'gamepad right stick y')])

    def input(key):
        print('key:', key)

    app.run()



input_handler.joystick = None
input_handler.joysticks = base.devices.getDevices(InputDevice.DeviceClass.flight_stick)
if input_handler.joysticks:
    input_handler.joystick = input_handler.joysticks[0]


for i, joystick in enumerate(input_handler.joysticks):
    joystick_name = 'joystick'
    if i > 0:
        joystick_name += f'_{i}'

    base.attachInputDevice(joystick, prefix=joystick_name)
    buttons = {
        'face_a' : 'a',
        'face_b' : 'b',
        'face_x' : 'x',
        'face_y' : 'y',
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
        base.accept(f'{joystick_name}-{original_name}', base.input, extraArgs=[f'{joystick_name} {new_name}'])
        base.accept(f'{joystick_name}-{original_name}-up', base.input, extraArgs=[f'{joystick_name} {new_name} up'])
        # print(original_name, new_name)

def update():
    for i, joystick in enumerate(input_handler.joysticks):
        joystick_name = 'joystick'
        if i > 0:
            joystick_name += f'_{i}'

        # Pole the axes
        for axis in joystick.axes:
            axis_name = axis.axis.name.lower()
            value = axis.value
            if abs(value) < .01:
                value = 0
            held_keys[f'{joystick_name} {axis_name}'] = value

Entity(name='joystick_handler', update=update, eternal=True) # connect update() to an entity so it runs
