from ursina import *
from ursina.scripts.property_generator import generate_properties_for_class


class ContentTypes:
    int = '0123456789'
    float = int + '.,'
    int_math = int + '+-*/'
    math = float + '+-*/'

@generate_properties_for_class()
class InputField(Button):
    def __init__(self, default_value='', label='', max_lines=1, character_limit=24, text='', text_color=None, active=False, **kwargs):
        if not 'scale' in kwargs and not 'scale_y' in kwargs:
            kwargs['scale'] = (kwargs.get('scale_x', .5), Text.size*2*max_lines)


        super().__init__(highlight_scale=1, pressed_scale=1, highlight_color=color.black, **kwargs)
        for key, value in kwargs.items():
            if 'scale' in key:
                setattr(self, key, value)

        self.default_value = default_value
        self.limit_content_to = None
        self.hide_content = False   # if set to True, will display content as '*'. can also be set to character instead of True.

        self.next_field = None
        self.submit_on = []   # for example: self.submit_on = ['enter', ] will call self.on_submit when you press enter.
        self.on_submit = None   # function to be called when you press self.submit_on.
        self.on_value_changed = None

        self.text_field = TextField(world_parent=self, x=-.45, y=.25, z=-.1, max_lines=max_lines, character_limit=character_limit, text=text, register_mouse_input=True, highlight_color=hsv(200,1,1,.5))
        destroy(self.text_field.bg)
        self.text_field.bg = self

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

            if self.on_value_changed and not self.text_field.text_entity.text == self.text_field.text:
                self.on_value_changed()
            self.text_field.text_entity.text = self.text_field.text

        self.text_field.render = render

        self.text_field.scale *= 1.25
        self.text_field.text = default_value
        self.text_field.render()
        self.text_field.shortcuts['indent'] = ('')
        self.text_field.shortcuts['dedent'] = ('')

        self.active = active

        if label:
            self.label = Text(str(label) + ':', parent = self, position = self.text_field.position, scale = 1.25)
            self.text_field.x += 0.1 * (len(str(label)) + 1.0) / 6.0

        for key, value in kwargs.items():
            setattr(self, key, value)


    def input(self, key):
        if key == 'tab' and self.text_field.cursor.y >= self.text_field.max_lines-1 and self.active:
            self.active = False
            if self.next_field:
                mouse.position = self.next_field.get_position(relative_to=camera.ui)
                invoke(setattr, self.next_field, 'active', True, delay=.01)

        if self.active and key in self.submit_on and self.on_submit:
            self.on_submit()
            self.active = False

        if self.active:
            self.text_field.input(key)
            return True # eat input when entering text to prevent unwanted actions while typing.


    def text_getter(self):
        return self.text_field.text

    def text_setter(self, value):
        self.text_field.text = ''
        self.text_field.cursor.position = (0,0)
        self.text_field.add_text(value, move_cursor=True)
        self.text_field.render()


    def text_color_getter(self):
        return self.text_field.text_entity.color
    def text_color_setter(self, value, temp=False):
        if hasattr(self, 'text_color'):
            self.text_field.text_entity.color = value

    def active_getter(self):
        return self.text_field.active
    def active_setter(self, value):
        self.text_field.active = value

    # def text_origin_setter(self, value):
    #     self.text_field.text_entity.text_origin = value


if __name__ == '__main__':
    app = Ursina()
    # window.fullscreen_size = (1366, 768)
    # background = Entity(model='quad', texture='pixelscape_combo', parent=camera.ui, scale=(camera.aspect_ratio,1), color=color.white)
    gradient = Entity(model='quad', texture='vertical_gradient', parent=camera.ui, scale=(camera.aspect_ratio,1), color=color.hsv(240,.6,.1,.75))

    username_field = InputField(y=-.12, limit_content_to='0123456789', default_value='11', active=True, scale_x=1)
    username_field.text = '0929468098'
    password_field = InputField(y=-.18, hide_content=True)
    username_field.next_field = password_field

    def submit():
        print('ursername:', username_field.text)
        print('password:',  password_field.text)

    Button(text='Login', scale=.1, color=color.cyan.tint(-.4), y=-.26, on_click=submit).fit_to_text()
    username_field.on_value_changed = submit
    app.run()
