from ursina import *

class ExitButton(Button):
    def __init__(self, **kwargs):
        super().__init__(
            eternal = True,
            parent = scene.ui,
            scale = (.025, .025),
            position = Vec2(window.top_right) - Vec2(.0125, .0125),
            model = 'quad',
            color = color.red,
            text = 'x',
            **kwargs)


    def on_click(self):
        os._exit(0)

    def input(self, key):
        if held_keys['shift'] and key == 'q':
            self.on_click()


if __name__ == '__main__':
    app = Ursina().run()
