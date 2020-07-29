from ursina import *


class InputField(Button):

    def __init__(self, default_value='', label='', max_lines=1, **kwargs):
        super().__init__(
            scale=(.5, Text.size * 2),
            highlight_scale = 1,
            pressed_scale = 1,
            )
        for key, value in kwargs.items():
            if 'scale' in key:
                setattr(self, key, value)

        self.default_value = default_value
        self.next_field = None

        self.text_field = TextField(world_parent=self, x=-.45, y=.3, z=-.1, max_lines=max_lines)
        self.text_field.scale *= 1.5
        self.text_field.text = default_value
        self.text_field.render()

        self.text_field.register_mouse_input = False
        self.active = False

        if label:
            self.label = Text('Label:')
            self.text_field.x += 5


        for key, value in kwargs.items():
            setattr(self, key, value)

    def input(self, key):
        if key == 'left mouse down':
            self.active = self.hovered

        if key == 'tab' and self.text_field.cursor.y >= self.text_field.max_lines-1 and self.active:
            self.active = False
            if self.next_field:
                mouse.position = self.next_field.get_position(relative_to=camera.ui)
                invoke(setattr, self.next_field, 'active', True, delay=.01)

    @property
    def text(self):
        return self.text_field.text

    @text.setter
    def text(self, value):
        self.text_field.text = ''
        self.text_field.cursor.position = (0,0)
        self.text_field.add_text(value, move_cursor=True)

    @property
    def active(self):
        return self._active

    @active.setter
    def active(self, value):
        print(value)
        self._active = value
        self.text_field.ignore = not value
        self.text_field.cursor.enabled = value
        # self.text_field.register_mouse_input = True
        # if value == True:
        #     # self.text_field.select_all()
        #     invoke(self.text_field.select_all, delay=.1)
        #     # self.text_field.input(' ')
        #     # self.text_field.erase()


if __name__ == '__main__':
    app = Ursina()
    input_field = InputField(default_value='ælol', max_lines=100)
    print(input_field.default_value)

    def submit():
        print(input_field.text)

    Button('submit', scale=.1, color=color.azure, y=-.2, on_click=submit).fit_to_text()

    app.run()
