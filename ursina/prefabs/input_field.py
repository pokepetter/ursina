from ursina import *


class InputField(Button):

    def __init__(self, **kwargs):
        super().__init__(
            scale=(.5, Text.size * 2),
            highlight_scale = 1,
            pressed_scale = 1,
            )
        for key, value in kwargs.items():
            if 'scale' in key:
                setattr(self, key, value)

        self.text_field = TextField(world_parent=self, x=-.45, y=.3, z=-.1, max_lines=1)
        self.text_field.scale *= 2
        self.active = False

        for key, value in kwargs.items():
            setattr(self, key, value)

    def input(self, key):
        if key == 'left mouse down':
            self.active = self.hovered

    @property
    def text(self):
        return self.text_field.texS

    @property
    def active(self):
        return self._active

    @active.setter
    def active(self, value):
        self.text_field.ignore = not value
        self.text_field.cursor.enabled = value


if __name__ == '__main__':
    app = Ursina()

    input_field = InputField()

    def submit():
        print(input_field.text)

    Button('submit', scale=.1, color=color.azure, y=-.2, on_click=submit).fit()

    app.run()
