from ursina import *
from panda3d.core import InputDevice

if __name__ == '__main__':
    app = Ursina()
    text_entity = Text()
    player = Entity(model='cube', color=color.azure)

    def update():
        player.x += held_keys['joystick yaw'] * time.dt * 5
        player.y += held_keys['joystick pitch'] * time.dt * 5
        text_entity.text = '\n'.join([f'{key}: {held_keys[key]}' for key in ('joystick trigger', 'joystick 2', )])

    def input(key):
        print('key:', key)

    app.run()

button_name = lambda button: button.handle.name.replace('_', ' ').replace('joystick', '')
JITTER = .01

input_handler.joystick = None
input_handler.joysticks = base.devices.getDevices(InputDevice.DeviceClass.flight_stick)
if input_handler.joysticks:
    input_handler.joystick = input_handler.joysticks[0]


for i, joystick in enumerate(input_handler.joysticks):
    joystick_name = 'joystick'
    if i > 0:
        joystick_name += f'_{i}'

    base.attachInputDevice(joystick, prefix=joystick_name)
    
    for button in joystick.buttons:
        name = button_name(button)
        original_name = button.handle.name
        base.accept(f'{joystick_name}-{original_name}', base.input, extraArgs=[f'{joystick_name} {name}'])
        base.accept(f'{joystick_name}-{original_name}-up', base.input, extraArgs=[f'{joystick_name} {name} up'])

def update():
    for i, joystick in enumerate(input_handler.joysticks):
        joystick_name = 'joystick'
        if i > 0:
            joystick_name += f'_{i}'

        # Poll the axes
        for axis in joystick.axes:
            axis_name = axis.axis.name.lower()
            value = axis.value
            if abs(value) < JITTER:
                value = 0
            held_keys[f'{joystick_name} {axis_name}'] = value
        for button in joystick.buttons:
            name = button_name(button)
            pressed = button.pressed
            held_keys[f'{joystick_name} {name}'] = int(pressed)

Entity(name='joystick_handler', update=update, eternal=True) # connect update() to an entity so it runs
