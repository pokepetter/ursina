from ursina import *

class ExitButton(Button):
    def __init__(self, **kwargs):
        super().__init__(
            eternal = True,
            parent = scene.ui,
            position = window.top_right,
            scale = (.025, .025),
            color = color.red,
            text = 'x',
            origin = (.5, .5),
            **kwargs)


    def on_click(self):
        os._exit(0)

    def input(self, key):
        if held_keys['shift'] and key == 'q':
            self.on_click()


if __name__ == '__main__':
    app = Ursina().run()
