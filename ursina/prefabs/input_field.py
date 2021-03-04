from ursina import *
from enum import Enum

class ContentTypes:
    int = '0123456789'
    float = int + '.,'
    math = float + '+-*/'


class InputField(Button):
    def __init__(self, default_value='', label='', max_lines=1, **kwargs):
        super().__init__(
            scale=(.5, Text.size * 2),
            highlight_scale = 1,
            pressed_scale = 1,
            highlight_color = color.black
            )
        for key, value in kwargs.items():
            if 'scale' in key:
                setattr(self, key, value)

        self.default_value = default_value
        self.limit_content_to = None
        self.hide_content = False   # if set to True, will display content as '*'. can also be set to character instead of True.

        self.next_field = None

        self.text_field = TextField(world_parent=self, x=-.45, y=.3, z=-.1, max_lines=max_lines)
        def render():
            if self.limit_content_to:
                org_length = len(self.text_field.text)
                self.text_field.text = ''.join([e for e in self.text_field.text if e in self.limit_content_to])
                self.text_field.cursor.x -= org_length - len(self.text_field.text)
                self.text_field.cursor.x = max(0, self.text_field.cursor.x)

            if self.hide_content:
                replacement_char = '*'
                if isinstance(self.hide_content, str):
                    replacement_char = self.hide_content

                self.text_field.text_entity.text = replacement_char * len(self.text_field.text)
                return

            self.text_field.text_entity.text = self.text_field.text

        self.text_field.render = render

        self.text_field.scale *= 1.25
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
    # window.fullscreen_size = (1366, 768)
    background = Sprite('shore', color=color.dark_gray)
    username_field = InputField()
    password_field = InputField(y=-.06, hide_content=True)
    username_field.next_field = password_field

    def submit():
        print('ursername:', username_field.text)
        print('password:',  password_field.text)

    Button('Login', scale=.1, color=color.azure, y=-.14, on_click=submit).fit_to_text()

    app.run()
