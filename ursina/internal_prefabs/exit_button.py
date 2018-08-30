from ursina import *

class ExitButton(Button):
    def __init__(self):
        super().__init__(
            eternal = True,
            parent = scene.ui,
            name = 'exit_button_entity',
            origin = (.5, .5),
            position = window.top_right,
            scale = (.025, .025),
            color = color.red,
            text = 'X',
            enabled = True,
            )
    def on_click(self):
        os._exit(0)

    def input(self, key):
        if held_keys['shift'] and key == 'q':
            self.on_click()
